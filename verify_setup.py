#!/usr/bin/env python3
"""
Verification script to check if everything is set up correctly
"""

import sys
import os
from pathlib import Path

def check_imports():
    """Check if all required packages are installed"""
    print("\n[1] Checking Python packages...")
    print("-" * 60)
    
    packages = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'sentencepiece': 'SentencePiece',
        'tqdm': 'TQDM',
    }
    
    missing = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name:20} installed")
        except ImportError:
            print(f"✗ {name:20} NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def check_files():
    """Check if all project files exist"""
    print("\n[2] Checking project files...")
    print("-" * 60)
    
    required_files = [
        'train.py',
        'dataset.py',
        'data_prep.py',
        'setup_tokenizer.py',
        'run_training.py',
        'requirements.txt',
        'README.md',
    ]
    
    missing = []
    
    for filepath in required_files:
        if Path(filepath).exists():
            print(f"✓ {filepath:30} exists")
        else:
            print(f"✗ {filepath:30} NOT found")
            missing.append(filepath)
    
    if missing:
        print(f"\nMissing files: {', '.join(missing)}")
        return False
    
    return True


def check_model():
    """Check if model can be instantiated"""
    print("\n[3] Checking model instantiation...")
    print("-" * 60)
    
    try:
        import torch
        from train import Config, LLM
        
        # Create config
        cfg = Config()
        print(f"✓ Config created (device: {cfg.device})")
        
        # Create model
        model = LLM(cfg)
        print(f"✓ Model created")
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        print(f"✓ Model parameters: {total_params / 1e6:.1f}M")
        
        # Test forward pass
        x = torch.randint(0, cfg.vocab_size, (2, cfg.seq_len))
        output = model(x)
        print(f"✓ Forward pass successful, output shape: {output.shape}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_tokenizer():
    """Check if tokenizer can be set up"""
    print("\n[4] Checking tokenizer...")
    print("-" * 60)
    
    try:
        import sentencepiece as spm
        
        tokenizer_file = Path("tokenizers/tokenizer.model")
        
        if tokenizer_file.exists():
            sp = spm.SentencePieceProcessor(model_file=str(tokenizer_file))
            vocab_size = sp.get_piece_size()
            print(f"✓ Tokenizer loaded, vocab size: {vocab_size}")
        else:
            print(f"⚠ Tokenizer not trained yet (expected at {tokenizer_file})")
            print(f"  Run: python setup_tokenizer.py")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_data():
    """Check if training data exists"""
    print("\n[5] Checking training data...")
    print("-" * 60)
    
    data_dir = Path("data/processed")
    
    if not data_dir.exists():
        print(f"⚠ Data directory not found: {data_dir}")
        print(f"  Run: python data_prep.py")
        return False
    
    files = {
        'combined.txt': 'Combined dataset',
        'train.txt': 'Training set',
        'val.txt': 'Validation set',
        'test.txt': 'Test set',
    }
    
    found = {}
    for filename, description in files.items():
        filepath = data_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size / (1024**2)
            print(f"✓ {description:20} ({size:.1f} MB)")
            found[filename] = True
        else:
            print(f"⚠ {description:20} not found")
            found[filename] = False
    
    if not any(found.values()):
        print(f"\nNo data found. Run: python data_prep.py")
        return False
    
    return True


def check_gpu():
    """Check GPU availability"""
    print("\n[6] Checking GPU...")
    print("-" * 60)
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✓ GPU available")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  Device count: {torch.cuda.device_count()}")
        else:
            print(f"⚠ GPU not available (using CPU)")
            print(f"  For faster training, ensure CUDA is installed")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("LLM Training Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Packages", check_imports),
        ("Project Files", check_files),
        ("Model", check_model),
        ("Tokenizer", check_tokenizer),
        ("Training Data", check_data),
        ("GPU", check_gpu),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}  {name}")
    
    # Next steps
    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    
    if not results["Training Data"]:
        print("1. Prepare training data:")
        print("   python data_prep.py")
    
    if not results["Tokenizer"]:
        print("2. Train tokenizer:")
        print("   python setup_tokenizer.py")
    
    print("3. Start training:")
    print("   python run_training.py --mode train")
    
    print("4. Generate text:")
    print("   python run_training.py --mode generate --prompt 'Hello world'")
    
    print("\nFor more info, see: README.md")
    
    # Exit code
    all_pass = all(results.values())
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
