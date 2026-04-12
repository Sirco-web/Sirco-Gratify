#!/usr/bin/env python3
"""
Demo script showing how to use all components
Run this to see the complete workflow
"""

import torch
from pathlib import Path
import sys


def demo_basic_model():
    """Demo 1: Create and test a basic model"""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Model Test")
    print("=" * 60)
    
    from train import Config, LLM
    
    # Create config
    cfg = Config()
    cfg.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Create model
    model = LLM(cfg).to(cfg.device)
    model.eval()
    
    print(f"\nModel created on {cfg.device}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")
    
    # Test forward pass
    x = torch.randint(0, cfg.vocab_size, (1, cfg.seq_len)).to(cfg.device)
    with torch.no_grad():
        logits = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {logits.shape}")
    print("✓ Forward pass successful!")
    
    return model, cfg


def demo_tokenizer():
    """Demo 2: Create dummy tokenizer and test"""
    print("\n" + "=" * 60)
    print("Demo 2: Tokenizer Test")
    print("=" * 60)
    
    tokenizer_file = Path("tokenizers/tokenizer.model")
    
    if tokenizer_file.exists():
        import sentencepiece as spm
        
        tokenizer = spm.SentencePieceProcessor(model_file=str(tokenizer_file))
        vocab_size = tokenizer.get_piece_size()
        
        print(f"\nTokenizer loaded: {tokenizer_file}")
        print(f"Vocabulary size: {vocab_size}")
        
        # Test encoding/decoding
        test_text = "Hello, how are you today?"
        tokens = tokenizer.encode(test_text)
        decoded = tokenizer.decode(tokens)
        
        print(f"\nTest text: {test_text}")
        print(f"Tokens ({len(tokens)}): {tokens[:10]}...")
        print(f"Decoded: {decoded}")
        print("✓ Tokenizer working!")
        
        return tokenizer
    else:
        print(f"\n⚠ Tokenizer not found: {tokenizer_file}")
        print("Run: python setup_tokenizer.py")
        return None


def demo_generation(model, tokenizer, cfg):
    """Demo 3: Text generation"""
    print("\n" + "=" * 60)
    print("Demo 3: Text Generation")
    print("=" * 60)
    
    if model is None or tokenizer is None:
        print("Model or tokenizer not available, skipping...")
        return
    
    from train import generate
    
    prompts = [
        "The future of AI is",
        "Machine learning is",
        "Artificial intelligence",
    ]
    
    print("\nGenerating text...")
    for prompt in prompts:
        try:
            output = generate(model, tokenizer, prompt, max_new_tokens=50)
            print(f"\nPrompt: {prompt}")
            print(f"Output: {output}\n")
        except Exception as e:
            print(f"Error: {e}")


def demo_dataset_structure():
    """Demo 4: Dataset structure"""
    print("\n" + "=" * 60)
    print("Demo 4: Dataset Structure")
    print("=" * 60)
    
    from dataset import TextDataset, CachedTextDataset
    
    print("\nDataset classes available:")
    print("  - TextDataset: Basic dataset with on-the-fly tokenization")
    print("  - CachedTextDataset: Faster with pre-computed cache")
    print("  - StreamingTextDataset: Memory-efficient streaming")
    print("  - create_dataloader(): Creates PyTorch DataLoader")
    
    print("\nUsage example:")
    print("""
    from dataset import create_dataloader
    from train import Config
    
    cfg = Config()
    dataloader = create_dataloader(
        'data/processed/train.txt',
        tokenizer,
        batch_size=32,
        seq_len=256
    )
    
    for x, y in dataloader:
        # x: input token ids
        # y: target token ids (shifted by 1)
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, vocab_size), y.reshape(-1))
    """)


def demo_training_structure():
    """Demo 5: Training structure"""
    print("\n" + "=" * 60)
    print("Demo 5: Training Components")
    print("=" * 60)
    
    from train import Config, LLM, train, evaluate
    
    print("\nTraining workflow:")
    print("  1. Load or create config (train.py)")
    print("  2. Create model instance")
    print("  3. Load/create tokenizer")
    print("  4. Create datasets")
    print("  5. Run training loop")
    print("  6. Save checkpoints")
    
    print("\nTraining function signature:")
    print("""
    train(
        model,
        train_data,
        val_data,
        cfg,
        tokenizer=None
    )
    """)
    
    print("\nEvaluation function signature:")
    print("""
    evaluate(
        model,
        val_data,
        cfg,
        max_batches=10
    )
    """)


def demo_full_pipeline():
    """Demo 6: Full training pipeline"""
    print("\n" + "=" * 60)
    print("Demo 6: Full Training Pipeline")
    print("=" * 60)
    
    print("""
The complete training pipeline:

Step 1: Prepare data
    python data_prep.py
    -> Creates data/processed/train.txt, val.txt, test.txt

Step 2: Train tokenizer
    python setup_tokenizer.py
    -> Creates tokenizers/tokenizer.model

Step 3: Start training
    python run_training.py --mode train
    -> Trains the model and saves checkpoints

Step 4: Generate text
    python run_training.py --mode generate --prompt "Hello"
    -> Generates continuations from prompts

Step 5: Interactive chat
    python run_training.py --mode chat
    -> Chat with the trained model

See README.md for detailed instructions!
    """)


def main():
    """Run all demos"""
    print("=" * 60)
    print("LLM Training - Complete Demo")
    print("=" * 60)
    
    # Demo 1: Basic model
    try:
        model, cfg = demo_basic_model()
    except Exception as e:
        print(f"Error in demo 1: {e}")
        model, cfg = None, None
    
    # Demo 2: Tokenizer
    try:
        tokenizer = demo_tokenizer()
    except Exception as e:
        print(f"Error in demo 2: {e}")
        tokenizer = None
    
    # Demo 3: Generation
    if model and tokenizer:
        try:
            demo_generation(model, tokenizer, cfg)
        except Exception as e:
            print(f"Error in demo 3: {e}")
    
    # Demo 4: Dataset structure
    try:
        demo_dataset_structure()
    except Exception as e:
        print(f"Error in demo 4: {e}")
    
    # Demo 5: Training structure
    try:
        demo_training_structure()
    except Exception as e:
        print(f"Error in demo 5: {e}")
    
    # Demo 6: Full pipeline
    try:
        demo_full_pipeline()
    except Exception as e:
        print(f"Error in demo 6: {e}")
    
    print("\n" + "=" * 60)
    print("Demos complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python verify_setup.py")
    print("2. Run: python data_prep.py")
    print("3. Run: python setup_tokenizer.py")
    print("4. Run: python run_training.py --mode train")


if __name__ == "__main__":
    main()
