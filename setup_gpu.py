#!/usr/bin/env python3
"""
Smart GPU Setup Script for Gratify LLM
Automatically detects GPU and installs correct PyTorch version
"""

import subprocess
import sys
import platform


def run_command(cmd, description=None):
    """Run a shell command and return success status."""
    if description:
        print(f"\n{'='*60}")
        print(f"📦 {description}")
        print(f"{'='*60}")
    
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def check_gpu():
    """Check if GPU is available."""
    print("\n🔍 Checking for GPU support...")
    
    try:
        # Try to run nvidia-smi
        result = subprocess.run(
            "nvidia-smi --query-gpu=name --format=csv,noheader",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            gpu_name = result.stdout.strip()
            print(f"✅ GPU Found: {gpu_name}")
            return "nvidia"
        else:
            print("⚠️  NVIDIA GPU not detected")
            return None
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return None


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🚀 Gratify LLM - Smart GPU Setup                    ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    # Check OS
    os_type = platform.system()
    print(f"\n🖥️  Operating System: {os_type}")
    
    # Check GPU
    gpu_type = check_gpu()
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install PyTorch with GPU support
    if gpu_type == "nvidia":
        print("\n✅ Installing PyTorch with NVIDIA GPU support (CUDA 12.1)...")
        
        # Use CUDA 12.1 (compatible with your CUDA 13.0)
        pytorch_cmd = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
        
        if run_command(pytorch_cmd, "Installing PyTorch with GPU support"):
            print("✅ PyTorch GPU installation successful!")
        else:
            print("❌ PyTorch installation failed. Trying fallback...")
            run_command(f"{sys.executable} -m pip install torch torchvision torchaudio", "Fallback PyTorch installation")
    else:
        print("\n⚠️  No GPU detected. Installing CPU version...")
        
        pytorch_cmd = f"{sys.executable} -m pip install torch torchvision torchaudio"
        run_command(pytorch_cmd, "Installing PyTorch (CPU)")
    
    # Install other requirements
    other_packages = [
        "numpy",
        "tqdm",
    ]
    
    for package in other_packages:
        run_command(
            f"{sys.executable} -m pip install {package}",
            f"Installing {package}"
        )
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    
    # Verify installation
    print("\n🧪 Verifying installation...")
    verify_code = """
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name()}")
    print(f"GPU Count: {torch.cuda.device_count()}")
else:
    print("Using CPU mode")
"""
    
    result = subprocess.run(
        [sys.executable, "-c", verify_code],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Warnings/Errors:", result.stderr)
    
    print("\n" + "="*60)
    print("🚀 Next Steps:")
    print("="*60)
    print("1. Run: python test_system.py")
    print("2. Train: python src/train.py --epochs 10")
    print("3. Chat: python src/cli.py")
    print("\n✨ Your GPU should now be detected!")


if __name__ == "__main__":
    main()
