#!/usr/bin/env python3
"""
Smart GPU Setup Script for Gratify LLM
Automatically detects GPU/OS and installs the best acceleration backend:
- NVIDIA: CUDA-enabled PyTorch wheels (bundled CUDA runtime)
- AMD (Linux): ROCm wheels when compatible
- Apple Silicon: MPS (no CUDA on macOS)
- Fallback: CPU
"""

from __future__ import annotations

import subprocess
import sys
import platform
import shutil
import os
from dataclasses import dataclass
from typing import Optional, Sequence


def run_command(cmd: Sequence[str] | str, description: str | None = None) -> bool:
    """Run a command and return success status."""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}")

    shell = isinstance(cmd, str)
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell)
    return result.returncode == 0


def run_capture(cmd: Sequence[str] | str) -> subprocess.CompletedProcess:
    shell = isinstance(cmd, str)
    return subprocess.run(cmd, shell=shell, capture_output=True, text=True)


@dataclass(frozen=True)
class SystemInfo:
    os_type: str
    is_windows: bool
    is_linux: bool
    is_macos: bool
    python: str


@dataclass(frozen=True)
class GpuInfo:
    vendor: Optional[str]  # "nvidia" | "amd" | "apple" | None
    name: Optional[str]
    details: Optional[str] = None


def in_venv() -> bool:
    # Works for venv/virtualenv.
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix


def ensure_venv(sysinfo: SystemInfo) -> None:
    """
    Ensure we're running in a project-local virtual environment.

    This avoids:
    - PEP 668 "externally-managed-environment" on Debian/Ubuntu Python
    - Permission/admin issues on Windows/macOS system Python
    """
    if in_venv():
        return

    # Prevent infinite recursion if something goes wrong.
    if os.environ.get("GRATIFY_SETUP_GPU_IN_VENV") == "1":
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(project_root, ".venv")

    print("\nCreating/using a project virtual environment at .venv (recommended for all OSes).")
    if not os.path.isdir(venv_dir):
        ok = run_command([sysinfo.python, "-m", "venv", venv_dir], description="Creating virtual environment")
        if not ok:
            print("Failed to create venv. On Ubuntu/Debian you may need: apt install python3-venv")
            return

    venv_python = os.path.join(venv_dir, "Scripts", "python.exe") if sysinfo.is_windows else os.path.join(venv_dir, "bin", "python")
    if not os.path.isfile(venv_python):
        print(f"Virtual environment python not found at: {venv_python}")
        return

    env = os.environ.copy()
    env["GRATIFY_SETUP_GPU_IN_VENV"] = "1"

    print(f"Re-running inside venv: {venv_python}")
    os.execve(venv_python, [venv_python, os.path.abspath(__file__), *sys.argv[1:]], env)


def get_system_info() -> SystemInfo:
    os_type = platform.system()
    return SystemInfo(
        os_type=os_type,
        is_windows=os_type == "Windows",
        is_linux=os_type == "Linux",
        is_macos=os_type == "Darwin",
        python=sys.executable,
    )


def detect_nvidia() -> Optional[GpuInfo]:
    # Prefer an explicit path lookup to avoid misleading stderr.
    if shutil.which("nvidia-smi") is None:
        return None

    result = run_capture(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"])
    if result.returncode != 0:
        return None

    line = result.stdout.strip().splitlines()[0].strip() if result.stdout.strip() else ""
    if not line:
        return GpuInfo(vendor="nvidia", name=None, details=None)

    # "GPU Name, 551.86"
    parts = [p.strip() for p in line.split(",")]
    name = parts[0] if parts else None
    driver = parts[1] if len(parts) > 1 else None
    details = f"driver={driver}" if driver else None
    return GpuInfo(vendor="nvidia", name=name, details=details)


def detect_apple_gpu(sysinfo: SystemInfo) -> Optional[GpuInfo]:
    if not sysinfo.is_macos:
        return None
    # macOS has no CUDA; we treat Apple GPUs as "apple" for MPS.
    return GpuInfo(vendor="apple", name="Apple GPU (MPS)")


def detect_amd_linux(sysinfo: SystemInfo) -> Optional[GpuInfo]:
    if not sysinfo.is_linux:
        return None
    # Best-effort detection without hard dependencies.
    if shutil.which("rocminfo") is not None:
        r = run_capture(["rocminfo"])
        if r.returncode == 0 and ("AMD" in r.stdout or "gfx" in r.stdout):
            return GpuInfo(vendor="amd", name="AMD GPU (ROCm capable)")
    if shutil.which("lspci") is not None:
        r = run_capture(["lspci"])
        if r.returncode == 0 and ("VGA" in r.stdout or "3D controller" in r.stdout):
            # Heuristic: check for AMD/ATI.
            if "AMD" in r.stdout or "Advanced Micro Devices" in r.stdout or "ATI" in r.stdout:
                return GpuInfo(vendor="amd", name="AMD GPU (detected)")
    return None


def detect_gpu(sysinfo: SystemInfo) -> GpuInfo:
    print("\nChecking for GPU support...")

    nvidia = detect_nvidia()
    if nvidia:
        name = nvidia.name or "NVIDIA GPU"
        extra = f" ({nvidia.details})" if nvidia.details else ""
        print(f"Detected: {name}{extra}")
        return nvidia

    apple = detect_apple_gpu(sysinfo)
    if apple:
        print(f"Detected: {apple.name}")
        return apple

    amd = detect_amd_linux(sysinfo)
    if amd:
        print(f"Detected: {amd.name}")
        return amd

    print("No supported GPU detected (or drivers not installed).")
    return GpuInfo(vendor=None, name=None)


def pip_install(
    pkgs: list[str],
    extra_index_url: str | None = None,
    description: str | None = None,
    upgrade: bool = False,
    force_reinstall: bool = False,
    no_cache_dir: bool = False,
) -> bool:
    cmd: list[str] = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    if force_reinstall:
        cmd.append("--force-reinstall")
    if no_cache_dir:
        cmd.append("--no-cache-dir")
    if extra_index_url:
        cmd += ["--index-url", extra_index_url]
    cmd += pkgs
    return run_command(cmd, description=description)


def install_pytorch_for_gpu(sysinfo: SystemInfo, gpu: GpuInfo) -> None:
    # Important: "Installing CUDA stuff" is ambiguous. For most users, the goal is
    # *CUDA-enabled PyTorch* (which includes the CUDA runtime in the wheel).
    # A full system CUDA Toolkit install is not required for PyTorch usage.

    if gpu.vendor == "nvidia":
        print("\nNVIDIA detected: installing CUDA-enabled PyTorch wheels (bundled CUDA runtime).")
        # Default to cu121 which is widely supported; torch will bundle CUDA runtime.
        # If a user has a very new driver, cu121 still typically works.
        # If a CPU-only torch is already installed, pip often keeps it because versions can look "satisfied".
        # Force reinstall from the CUDA index.
        ok = pip_install(
            ["torch", "torchvision", "torchaudio"],
            extra_index_url="https://download.pytorch.org/whl/cu121",
            description="Installing PyTorch (CUDA, cu121)",
            upgrade=True,
            force_reinstall=True,
            no_cache_dir=True,
        )
        if not ok:
            print("PyTorch CUDA install failed; falling back to CPU wheels.")
            ok2 = pip_install(
                ["torch", "torchvision", "torchaudio"],
                description="Installing PyTorch (CPU fallback)",
                upgrade=True,
                force_reinstall=True,
                no_cache_dir=True,
            )
            if not ok2:
                raise RuntimeError("Failed to install PyTorch (CUDA and CPU fallback).")
        return

    if gpu.vendor == "amd" and sysinfo.is_linux:
        # ROCm support is Linux-only and hardware-specific. We attempt a best-effort install.
        print("\nAMD GPU detected (Linux): attempting ROCm-enabled PyTorch install.")
        ok = pip_install(
            ["torch", "torchvision", "torchaudio"],
            extra_index_url="https://download.pytorch.org/whl/rocm6.0",
            description="Installing PyTorch (ROCm 6.0)",
            upgrade=True,
            force_reinstall=True,
            no_cache_dir=True,
        )
        if not ok:
            print("ROCm install failed; falling back to CPU wheels.")
            ok2 = pip_install(
                ["torch", "torchvision", "torchaudio"],
                description="Installing PyTorch (CPU fallback)",
                upgrade=True,
                force_reinstall=True,
                no_cache_dir=True,
            )
            if not ok2:
                raise RuntimeError("Failed to install PyTorch (ROCm and CPU fallback).")
        return

    if gpu.vendor == "apple":
        print("\nApple GPU detected: installing standard PyTorch (uses MPS on supported Macs).")
        ok = pip_install(
            ["torch", "torchvision", "torchaudio"],
            description="Installing PyTorch (macOS / MPS)",
            upgrade=True,
        )
        if not ok:
            raise RuntimeError("Failed to install PyTorch on macOS.")
        return

    print("\nInstalling CPU-only PyTorch (no GPU backend detected).")
    ok = pip_install(["torch", "torchvision", "torchaudio"], description="Installing PyTorch (CPU)", upgrade=True)
    if not ok:
        raise RuntimeError("Failed to install PyTorch (CPU).")


def print_driver_guidance(sysinfo: SystemInfo, gpu: GpuInfo) -> None:
    if gpu.vendor == "nvidia":
        return

    # If Windows and no NVIDIA detected, users often expect CUDA but are missing driver / nvidia-smi.
    if sysinfo.is_windows:
        print("\nWindows note:")
        print("- CUDA only works with NVIDIA GPUs and an installed NVIDIA driver.")
        print("- If you have an NVIDIA GPU but detection failed, install/update the NVIDIA driver, reboot, then rerun this script.")
        print("- This script focuses on getting a working PyTorch GPU stack; it does not install Windows display drivers.")


def verify_installation(expected_gpu_vendor: Optional[str] = None) -> None:
    print("\n" + "=" * 60)
    print("Verifying installation...")
    print("=" * 60)

    verify_code = r"""
import os
import torch

print(f"PyTorch: {torch.__version__}")
print(f"torch.version.cuda: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA devices: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"CUDA device 0: {torch.cuda.get_device_name(0)}")

# MPS (Apple)
has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
print(f"MPS available: {has_mps}")

# Basic tensor op to force initialization
device = "cuda" if torch.cuda.is_available() else ("mps" if has_mps else "cpu")
x = torch.randn(1024, 1024, device=device)
y = x @ x.T
print(f"Sanity matmul device: {y.device}")
"""

    result = subprocess.run([sys.executable, "-c", verify_code], capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout)
    if result.returncode != 0:
        print("Verification failed:")
        if result.stderr.strip():
            print(result.stderr)
        raise RuntimeError("Verification failed (PyTorch import or backend init failed).")
    if result.stderr.strip():
        print("Warnings/Errors:")
        print(result.stderr)

    # If we detected NVIDIA, require a CUDA build + runtime availability.
    if expected_gpu_vendor == "nvidia":
        # CUDA build wheels show +cuXXX in __version__ and torch.version.cuda is set.
        # torch.cuda.is_available() requires a working NVIDIA driver.
        # We assert both to avoid "installed CUDA index but kept +cpu build".
        if "+cu" not in result.stdout and "torch.version.cuda: None" in result.stdout:
            raise RuntimeError(
                "NVIDIA GPU detected but PyTorch is a CPU build.\n"
                "Fix by forcing reinstall from CUDA wheels:\n"
                "  python -m pip install --upgrade --force-reinstall --no-cache-dir "
                "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            )
        if "CUDA available: False" in result.stdout:
            raise RuntimeError(
                "PyTorch CUDA build installed, but CUDA is not available at runtime.\n"
                "This usually means the NVIDIA driver isn't installed/working (or needs a reboot)."
            )


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Gratify LLM - Smart GPU Setup                       ║")
    print("╚════════════════════════════════════════════════════════╝")

    sysinfo = get_system_info()
    print(f"\nOperating System: {sysinfo.os_type}")

    ensure_venv(sysinfo)

    gpu = detect_gpu(sysinfo)

    print("\nUpgrading pip...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip")

    try:
        install_pytorch_for_gpu(sysinfo, gpu)
    except RuntimeError as e:
        print("\n" + "=" * 60)
        print("Install failed.")
        print("=" * 60)
        print(str(e))
        print("\nCommon fixes:")
        print("- Ensure you have internet access (pip must reach PyPI / PyTorch wheels).")
        print("- If behind a proxy, configure it for pip (PIP_PROXY / HTTPS_PROXY).")
        print("- On Windows for CUDA: install the latest NVIDIA driver, reboot, then rerun.")
        sys.exit(1)
    print_driver_guidance(sysinfo, gpu)

    # Install other requirements
    for package in ["numpy", "tqdm"]:
        ok = pip_install([package], description=f"Installing {package}")
        if not ok:
            print(f"Failed to install {package}. Check network/proxy and rerun.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Setup complete.")
    print("=" * 60)

    try:
        verify_installation(expected_gpu_vendor=gpu.vendor)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Next steps:")
    print("=" * 60)
    print("1. Run: python test_system.py")
    print("2. Train: python src/train.py --epochs 10")
    print("3. Chat: python src/cli.py")


if __name__ == "__main__":
    main()
