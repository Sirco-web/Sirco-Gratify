#!/usr/bin/env python3
"""Fine-tuning script for Gratify LLM - train on new data with existing model."""

import os
import sys
import argparse
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from gpu_utils import setup_gpu_if_available, get_device_string
from config import (
    GratifyConfig, SystemConfig, DATA_DIR, CHECKPOINTS_DIR,
    get_latest_checkpoint, increment_checkpoint_version,
)
from model import GratifyLLM
from train import TextDataset, Trainer, load_training_data


def finetune_model(
    checkpoint_path=None,
    data_dir=None,
    epochs=5,
    batch_size=16,
    learning_rate=5e-5,  # Lower LR for fine-tuning
):
    """Fine-tune an existing model on new data."""
    
    print(f"\n{'='*60}")
    print(f"🎓 Gratify LLM - Fine-tuning Mode")
    print(f"{'='*60}")
    
    # Setup GPU
    print("\n🔧 Checking GPU support...")
    # Fine-tuning must NOT install or modify dependencies (including GPU/CUDA).
    setup_gpu_if_available(install=False)
    device = torch.device(get_device_string())
    print(f"📍 Using device: {device}")
    
    # Load checkpoint
    if checkpoint_path is None:
        checkpoint_path = get_latest_checkpoint()
    
    if checkpoint_path is None:
        print("❌ Error: No checkpoints found!")
        print("   Train model first using: python src/train.py")
        return False
    
    print(f"\n📂 Loading checkpoint from: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Load config and model
    print("🧠 Loading model...")
    config = GratifyConfig.from_dict(checkpoint["config"])
    model = GratifyLLM(config).to(device)
    model.load_state_dict(checkpoint["model_state"])
    
    print(f"   Model parameters: {model.count_parameters():,}")
    
    # Load fine-tuning data
    if data_dir is None:
        finetune_data_dir = Path(DATA_DIR) / "finetune"
    else:
        finetune_data_dir = Path(data_dir)
    
    print(f"\n📚 Loading fine-tuning data from: {finetune_data_dir}")
    training_text = load_training_data(finetune_data_dir)
    
    if training_text is None:
        print("❌ No training data found!")
        return False
    
    # Create dataset
    print("🔄 Preparing dataset...")
    dataset = TextDataset(seq_length=config.max_seq_length, text=training_text)
    
    print(f"   Total tokens: {len(dataset.tokens):,}")
    print(f"   Sequences: {len(dataset):,}")
    
    # Override learning rate for fine-tuning
    config.learning_rate = learning_rate
    
    # Create trainer
    trainer = Trainer(model, config, device)
    
    # Override optimizer with lower learning rate
    trainer.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Create dataloader
    train_loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    
    # Fine-tuning loop
    print(f"\n{'='*60}")
    print(f"🎓 Fine-tuning Configuration")
    print(f"{'='*60}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate} (reduced for fine-tuning)")
    print(f"{'='*60}\n")
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        num_batches = 0
        
        for batch_idx, batch in enumerate(train_loader):
            loss = trainer.train_step(batch)
            epoch_loss += loss
            num_batches += 1
            
            # Print progress
            if (batch_idx + 1) % 10 == 0:
                avg_loss = epoch_loss / num_batches
                print(f"Epoch {epoch+1}/{epochs} | "
                      f"Batch {batch_idx+1}/{len(train_loader)} | "
                      f"Loss: {avg_loss:.4f} | "
                      f"Step: {trainer.global_step}")
            
            # Save checkpoint periodically
            if trainer.global_step % 500 == 0:
                new_version = increment_checkpoint_version()
                trainer.save_checkpoint(version=new_version)
        
        epoch_avg_loss = epoch_loss / num_batches if num_batches > 0 else 0
        print(f"\n✅ Epoch {epoch+1}/{epochs} completed. Avg Loss: {epoch_avg_loss:.4f}\n")
    
    # Final checkpoint
    new_version = increment_checkpoint_version()
    trainer.save_checkpoint(version=new_version)
    
    print(f"\n{'='*60}")
    print(f"🎉 Fine-tuning completed!")
    print(f"{'='*60}\n")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fine-tune Gratify LLM on new data"
    )
    parser.add_argument(
        "--checkpoint", type=str, default=None,
        help="Path to checkpoint to fine-tune (default: latest)"
    )
    parser.add_argument(
        "--data-dir", type=str, default=None,
        help="Directory with training data (default: ./data)"
    )
    parser.add_argument(
        "--epochs", type=int, default=5,
        help="Number of fine-tuning epochs (default: 5)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=16,
        help="Batch size (default: 16)"
    )
    parser.add_argument(
        "--lr", type=float, default=5e-5,
        help="Learning rate for fine-tuning (default: 5e-5, lower than training)"
    )
    
    args = parser.parse_args()
    
    success = finetune_model(
        checkpoint_path=args.checkpoint,
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
