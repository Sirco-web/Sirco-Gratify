"""GPU detection and setup utilities for Gratify."""

import subprocess
import sys
import platform


def detect_gpu():
    """Detect if a GPU is available (CUDA or Metal)."""
    gpu_info = {
        "available": False,
        "type": None,
        "device_count": 0,
        "compute_capability": None,
    }

    # Check for NVIDIA CUDA
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info["available"] = True
            gpu_info["type"] = "CUDA"
            gpu_info["device_count"] = torch.cuda.device_count()
            if gpu_info["device_count"] > 0:
                gpu_info["compute_capability"] = torch.cuda.get_device_capability(0)
            return gpu_info
    except ImportError:
        pass

    # Check for AMD ROCm
    try:
        result = subprocess.run(
            ["rocm-smi"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            gpu_info["available"] = True
            gpu_info["type"] = "ROCm"
            # Count devices from rocm-smi output
            gpu_info["device_count"] = result.stdout.count("GPU")
            return gpu_info
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check for Apple Metal (macOS)
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "GPU" in result.stdout:
                gpu_info["available"] = True
                gpu_info["type"] = "Metal"
                gpu_info["device_count"] = 1
                return gpu_info
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return gpu_info


def install_gpu_dependencies(gpu_type):
    """Install GPU-specific dependencies."""
    print(f"\n🚀 Installing GPU support for {gpu_type}...")
    
    if gpu_type == "CUDA":
        print("Installing CUDA-enabled PyTorch...")
        packages = [
            "torch==2.1.1+cu121",
            "torchvision==0.16.1+cu121",
            "torchaudio==2.1.1+cu121",
        ]
        for package in packages:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", f"{package}", "-f", 
                 "https://download.pytorch.org/whl/torch_stable.html"],
                check=False
            )
        print("✅ CUDA dependencies installed!")
        
    elif gpu_type == "ROCm":
        print("Installing ROCm-enabled PyTorch...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "torch==2.1.1", "torchvision", "torchaudio"],
            check=False
        )
        print("✅ ROCm dependencies installed!")
        
    elif gpu_type == "Metal":
        print("Installing Metal-enabled PyTorch for macOS...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "torch==2.1.1", "torchvision", "torchaudio"],
            check=False
        )
        print("✅ Metal dependencies installed!")


def setup_gpu_if_available(install: bool = False):
    """Check for GPU and optionally install GPU dependencies."""
    gpu_info = detect_gpu()
    
    if gpu_info["available"]:
        print(f"\n✨ GPU DETECTED: {gpu_info['type']}")
        print(f"   Devices: {gpu_info['device_count']}")
        if gpu_info["compute_capability"]:
            print(f"   Compute Capability: {gpu_info['compute_capability']}")

        if install:
            install_gpu_dependencies(gpu_info["type"])
        else:
            print("ℹ️  Dependency installation is disabled for this run.")
            print("   This script will only use whatever torch backend is already installed.")
        return True
    else:
        print("\n⚠️  No GPU detected. Using CPU mode.")
        print("   For better performance, install:")
        print("   - NVIDIA GPU: Install CUDA Toolkit")
        print("   - AMD GPU: Install ROCm")
        print("   - Apple Silicon: Update PyTorch for Metal support")
        return False


def get_device_string():
    """Get the appropriate device string for PyTorch."""
    try:
        import torch
        if torch.cuda.is_available():
            return f"cuda:{torch.cuda.current_device()}"
    except ImportError:
        pass
    
    # Try Metal for macOS
    if platform.system() == "Darwin":
        try:
            import torch
            if torch.backends.mps.is_available():
                return "mps"
        except (ImportError, AttributeError):
            pass
    
    return "cpu"
