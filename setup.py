#!/usr/bin/env python3
"""Setup script for Gratify LLM with automatic GPU detection and installation."""

import subprocess
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gpu_utils import setup_gpu_if_available, detect_gpu


def install_base_requirements():
    """Install base requirements."""
    print("\n📦 Installing base requirements...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
        check=False
    )
    print("✅ Base requirements installed")


def setup_gpu():
    """Setup GPU support if available."""
    print("\n🔍 Detecting GPU...")
    gpu_info = detect_gpu()
    
    if not gpu_info["available"]:
        print("⚠️  No GPU detected. Proceeding with CPU-only setup.")
        return False
    
    print(f"\n✨ GPU Detected: {gpu_info['type']}")
    print(f"   Devices: {gpu_info['device_count']}")
    
    # Ask user if they want to install GPU support
    response = input("\nInstall GPU support? (y/n): ").lower().strip()
    if response not in ["y", "yes"]:
        print("Skipping GPU setup.")
        return False
    
    # Install GPU dependencies
    setup_gpu_if_available()
    return True


def create_sample_data():
    """Create sample training data."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Check if sample already exists
    sample_file = data_dir / "sample.md"
    if sample_file.exists():
        print("✅ Sample data already exists")
        return
    
    print("\n📝 Creating sample training data...")
    
    sample_content = """# Gratify by Sirco

Gratify is an AI language model trained from scratch with a focus on efficiency and simplicity.

## Features

- Character-level tokenization for flexibility
- Transformer-based architecture
- GPU acceleration support
- Checkpoint system with version tracking
- Interactive CLI for chatting
- Training from markdown files

## Getting Started

To train the model:
1. Add markdown files to the `data/` directory
2. Run `python src/train.py`
3. Chat with the model using `python src/cli.py`

## Model Architecture

The model uses:
- Positional encoding for sequence awareness
- Multi-head self-attention
- Feed-forward networks
- Layer normalization
- Residual connections

## GPU Support

Gratify automatically detects and uses GPU if available:
- NVIDIA CUDA for NVIDIA GPUs
- AMD ROCm for AMD GPUs
- Apple Metal for Apple Silicon

## Chat Interface

The CLI provides:
- Interactive conversation
- Chat history tracking
- Temperature control for generation
- Model information display

## Training Configuration

Default training uses:
- Adam optimizer
- Cross-entropy loss
- 4 transformer layers
- 8 attention heads
- 256-dimensional embeddings
- 512 token context length

## Checkpoint System

Each training session creates versioned checkpoints:
- `checkpoint_v1.pt` - First training run
- `checkpoint_v2.pt` - Continued training
- And so on...

Latest checkpoint is always saved as `latest_model.pt`

## Future Enhancements

- BPE tokenizer support
- Multi-GPU training
- Distributed training
- Model quantization
- Fine-tuning capabilities
"""
    
    with open(sample_file, "w") as f:
        f.write(sample_content)
    
    print(f"✅ Sample data created at {sample_file}")


def create_directories():
    """Create necessary directories."""
    dirs = [
        Path(__file__).parent / "data",
        Path(__file__).parent / "user_data",
        Path(__file__).parent / "checkpoints",
        Path(__file__).parent / "logs",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)
    
    print("✅ Directories created")


def print_welcome():
    """Print welcome message."""
    print("\n" + "="*60)
    print("🚀 Gratify LLM Setup")
    print("="*60)
    print("Training and inference platform for language models")
    print("By: Sirco")
    print("="*60)


def print_completion_message():
    """Print completion message with next steps."""
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\n📚 Next Steps:")
    print("1. Add markdown files to ./data/")
    print("2. Train the model:")
    print("   python src/train.py")
    print("\n3. Chat with the model:")
    print("   python src/cli.py")
    print("\n💡 Tips:")
    print("   - More training data = better model")
    print("   - Use --help flag with scripts for options")
    print("   - Check checkpoints/ for saved models")
    print("="*60 + "\n")


def main():
    """Main setup function."""
    print_welcome()
    
    # Create directories
    print("\n📂 Creating directories...")
    create_directories()
    
    # Install base requirements
    install_base_requirements()
    
    # Setup GPU
    setup_gpu()
    
    # Create sample data
    create_sample_data()
    
    # Print completion message
    print_completion_message()


if __name__ == "__main__":
    main()
