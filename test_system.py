#!/usr/bin/env python3
"""Quick test/demo script for Gratify LLM."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing imports...")
    try:
        from gpu_utils import detect_gpu, get_device_string
        print("   ✅ gpu_utils")
        
        from config import GratifyConfig, SYSTEM_BRAND
        print("   ✅ config")
        
        from model import GratifyLLM
        print("   ✅ model")
        
        import torch
        print("   ✅ torch")
        
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_gpu_detection():
    """Test GPU detection."""
    print("\n🔧 Testing GPU detection...")
    try:
        from gpu_utils import detect_gpu
        gpu_info = detect_gpu()
        
        if gpu_info["available"]:
            print(f"   ✅ GPU found: {gpu_info['type']}")
            print(f"      Devices: {gpu_info['device_count']}")
        else:
            print("   ⚠️  No GPU detected (CPU mode will be used)")
        
        return True
    except Exception as e:
        print(f"   ❌ GPU detection failed: {e}")
        return False


def test_config():
    """Test configuration."""
    print("\n⚙️ Testing configuration...")
    try:
        from config import GratifyConfig, SYSTEM_BRAND
        
        config = GratifyConfig()
        print(f"   ✅ Config loaded")
        print(f"      Model size: {config.embedding_dim}->vocab size: {config.vocab_size}")
        print(f"      Brand: {SYSTEM_BRAND['name']} by {SYSTEM_BRAND['author']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Config test failed: {e}")
        return False


def test_model_creation():
    """Test model creation."""
    print("\n🧠 Testing model creation...")
    try:
        import torch
        from config import GratifyConfig
        from model import GratifyLLM
        
        config = GratifyConfig()
        model = GratifyLLM(config)
        
        param_count = model.count_parameters()
        print(f"   ✅ Model created")
        print(f"      Parameters: {param_count:,}")
        
        # Test forward pass
        dummy_input = torch.randint(0, config.vocab_size, (1, 10))
        output = model(dummy_input)
        print(f"   ✅ Forward pass works")
        print(f"      Output shape: {output.shape}")
        
        return True
    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
        return False


def test_directories():
    """Test if required directories exist."""
    print("\n📁 Testing directories...")
    try:
        required_dirs = [
            Path(__file__).parent / "data",
            Path(__file__).parent / "user_data",
            Path(__file__).parent / "checkpoints",
            Path(__file__).parent / "src",
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                print(f"   ✅ {dir_path.name}/")
            else:
                print(f"   ❌ {dir_path.name}/ - MISSING")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Directory test failed: {e}")
        return False


def test_data():
    """Test if training data exists."""
    print("\n📚 Testing training data...")
    try:
        data_dir = Path(__file__).parent / "data"
        md_files = list(data_dir.glob("*.md"))
        
        if md_files:
            print(f"   ✅ Found {len(md_files)} markdown file(s)")
            total_size = sum(f.stat().st_size for f in md_files)
            print(f"      Total size: {total_size / 1024:.1f} KB")
            return True
        else:
            print("   ⚠️  No training data found")
            print("      Add .md files to data/ directory to train")
            return True  # Not a failure, just empty
    except Exception as e:
        print(f"   ❌ Data test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🧪 Gratify LLM - System Check                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Imports", test_imports),
        ("GPU Detection", test_gpu_detection),
        ("Configuration", test_config),
        ("Model Creation", test_model_creation),
        ("Directories", test_directories),
        ("Training Data", test_data),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ Everything looks good!")
        print("\n🚀 Next steps:")
        print("   1. python src/train.py        # Start training")
        print("   2. python src/cli.py          # Chat with model")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
