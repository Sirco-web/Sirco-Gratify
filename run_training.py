"""
Main training script for LLM
Orchestrates all components: model, data, training
"""

import torch
import torch.nn as nn
import argparse
from pathlib import Path
import os
import json
from datetime import datetime
import sentencepiece as spm

# Import components
from train import Config, LLM, train, evaluate, generate, save_model, chat
from dataset import create_dataloader
from setup_tokenizer import setup_tokenizer


class Trainer:
    """Main training coordinator"""
    
    def __init__(self, config):
        self.cfg = config
        self.device = torch.device(self.cfg.device)
        
        # Create output directory
        self.output_dir = Path(self.cfg.checkpoint_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize model
        self.model = None
        self.tokenizer = None
        self.dataloader_train = None
        self.dataloader_val = None
    
    def setup_tokenizer(self, data_dir="data/processed"):
        """Setup or load tokenizer"""
        print("\n" + "=" * 60)
        print("Setting up tokenizer...")
        print("=" * 60)
        
        tokenizer_file = Path("tokenizers/tokenizer.model")
        
        if tokenizer_file.exists():
            print(f"Loading tokenizer from {tokenizer_file}")
            self.tokenizer = spm.SentencePieceProcessor(model_file=str(tokenizer_file))
            print(f"✓ Tokenizer loaded (vocab size: {self.tokenizer.get_piece_size()})")
        else:
            # Try to train tokenizer
            combined_file = Path(data_dir) / "combined.txt"
            
            if combined_file.exists():
                print(f"Training new tokenizer on {combined_file}")
                self.tokenizer, tokenizer_file = setup_tokenizer(
                    data_file=combined_file,
                    vocab_size=self.cfg.vocab_size,
                    tokenizer_dir="tokenizers"
                )
            else:
                print(f"⚠ Data file not found: {combined_file}")
                print("Creating dummy tokenizer for demo...")
                # For demo without data, create dummy tokenizer
                self.tokenizer = None
    
    def setup_data(self, data_dir="data/processed"):
        """Setup data loaders"""
        print("\n" + "=" * 60)
        print("Setting up datasets...")
        print("=" * 60)
        
        if self.tokenizer is None:
            print("⚠ Tokenizer not available, skipping data setup")
            return
        
        data_dir = Path(data_dir)
        train_file = data_dir / "train.txt"
        val_file = data_dir / "val.txt"
        
        if not train_file.exists():
            print(f"⚠ Training data not found: {train_file}")
            print("Run: python data_prep.py")
            return
        
        # Create dataloaders
        self.dataloader_train = create_dataloader(
            str(train_file),
            self.tokenizer,
            batch_size=self.cfg.batch_size,
            seq_len=self.cfg.seq_len,
            split='train'
        )
        
        if val_file.exists():
            self.dataloader_val = create_dataloader(
                str(val_file),
                self.tokenizer,
                batch_size=self.cfg.batch_size,
                seq_len=self.cfg.seq_len,
                split='val'
            )
    
    def setup_model(self):
        """Initialize model"""
        print("\n" + "=" * 60)
        print("Initializing model...")
        print("=" * 60)
        
        self.model = LLM(self.cfg)
        self.model.to(self.device)
        
        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        print(f"Model initialized:")
        print(f"  Total parameters: {total_params / 1e6:.1f}M")
        print(f"  Trainable parameters: {trainable_params / 1e6:.1f}M")
        
        # Model config
        print(f"\nModel config:")
        print(f"  Dim: {self.cfg.dim}")
        print(f"  Heads: {self.cfg.heads}")
        print(f"  Layers: {self.cfg.layers}")
        print(f"  Vocab size: {self.cfg.vocab_size}")
        print(f"  Seq length: {self.cfg.seq_len}")
    
    def train(self):
        """Run training"""
        if self.model is None:
            print("Model not initialized!")
            return
        
        print("\n" + "=" * 60)
        print("Starting training...")
        print("=" * 60)
        
        if self.dataloader_train is None:
            print("⚠ No training data available")
            print("Run: python data_prep.py")
            return
        
        # Training loop
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.cfg.lr, weight_decay=0.1)
        scaler = torch.cuda.amp.GradScaler() if torch.cuda.is_available() else None
        
        best_val_loss = float('inf')
        step = 0
        
        print(f"Training for max {self.cfg.max_steps} steps")
        print(f"Saving checkpoints every {self.cfg.save_interval} steps")
        
        for epoch in range(self.cfg.num_epochs):
            print(f"\n[Epoch {epoch+1}/{self.cfg.num_epochs}]")
            
            for batch_idx, (x, y) in enumerate(self.dataloader_train):
                if step >= self.cfg.max_steps:
                    break
                
                x, y = x.to(self.device), y.to(self.device)
                
                # Training step
                self.model.train()
                
                with torch.cuda.amp.autocast() if torch.cuda.is_available() else torch.no_grad():
                    logits = self.model(x)
                    loss = torch.nn.functional.cross_entropy(
                        logits.view(-1, logits.size(-1)),
                        y.view(-1)
                    )
                
                optimizer.zero_grad()
                
                if scaler:
                    scaler.scale(loss).backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    optimizer.step()
                
                # Logging
                if step % 100 == 0:
                    print(f"  Step {step:5d} | Loss: {loss.item():.4f}")
                
                # Validation and checkpoint
                if step > 0 and step % self.cfg.save_interval == 0:
                    val_loss = None
                    
                    if self.dataloader_val:
                        val_loss = evaluate(self.model, self.dataloader_val, self.cfg, max_batches=10)
                        print(f"  Val Loss: {val_loss:.4f}")
                        
                        if val_loss < best_val_loss:
                            best_val_loss = val_loss
                    
                    # Save checkpoint
                    checkpoint_path = self.output_dir / f"model_step_{step}.pt"
                    torch.save({
                        'step': step,
                        'model': self.model.state_dict(),
                        'optimizer': optimizer.state_dict(),
                        'config': self.cfg.__dict__,
                    }, checkpoint_path)
                    
                    print(f"  Saved checkpoint: {checkpoint_path}")
                
                step += 1
            
            if step >= self.cfg.max_steps:
                break
        
        print(f"\n✓ Training complete!")
        print(f"Final model: {self.output_dir}")
    
    def evaluate_model(self):
        """Evaluate the model"""
        if self.model is None or self.dataloader_val is None:
            print("Model or validation data not available")
            return
        
        print("\n" + "=" * 60)
        print("Evaluating model...")
        print("=" * 60)
        
        val_loss = evaluate(self.model, self.dataloader_val, self.cfg, max_batches=100)
        print(f"Validation loss: {val_loss:.4f}")
    
    def generate_text(self, prompt="Hello", max_tokens=100):
        """Generate text from a prompt"""
        if self.model is None or self.tokenizer is None:
            print("Model or tokenizer not available")
            return
        
        print("\n" + "=" * 60)
        print("Generating text...")
        print("=" * 60)
        
        output = generate(self.model, self.tokenizer, prompt, max_new_tokens=max_tokens)
        print(f"Prompt: {prompt}")
        print(f"Output:\n{output}")
    
    def interactive_chat(self):
        """Start interactive chat"""
        if self.model is None or self.tokenizer is None:
            print("Model or tokenizer not available")
            return
        
        chat(self.model, self.tokenizer, self.cfg)
    
    def save_checkpoint(self, path=None):
        """Save model checkpoint"""
        if self.model is None:
            print("Model not initialized")
            return
        
        if path is None:
            path = self.output_dir / f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
        
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LLM Training from Scratch")
    
    parser.add_argument("--mode", type=str, default="train", 
                       choices=["train", "evaluate", "generate", "chat"],
                       help="Mode to run")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--seq_len", type=int, default=256, help="Sequence length")
    parser.add_argument("--dim", type=int, default=256, help="Model dimension")
    parser.add_argument("--heads", type=int, default=8, help="Number of attention heads")
    parser.add_argument("--layers", type=int, default=6, help="Number of layers")
    parser.add_argument("--checkpoint", type=str, help="Checkpoint to load")
    parser.add_argument("--prompt", type=str, default="The future of AI", 
                       help="Prompt for generation")
    parser.add_argument("--max_tokens", type=int, default=100, 
                       help="Max tokens to generate")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu",
                       help="Device to use")
    
    args = parser.parse_args()
    
    # Create config
    cfg = Config()
    cfg.batch_size = args.batch_size
    cfg.lr = args.lr
    cfg.num_epochs = args.epochs
    cfg.seq_len = args.seq_len
    cfg.dim = args.dim
    cfg.heads = args.heads
    cfg.layers = args.layers
    cfg.device = args.device
    
    # Create trainer
    trainer = Trainer(cfg)
    
    # Setup
    trainer.setup_tokenizer()
    trainer.setup_data()
    trainer.setup_model()
    
    # Run mode
    if args.mode == "train":
        trainer.train()
    elif args.mode == "evaluate":
        trainer.evaluate_model()
    elif args.mode == "generate":
        trainer.generate_text(prompt=args.prompt, max_tokens=args.max_tokens)
    elif args.mode == "chat":
        trainer.interactive_chat()
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
