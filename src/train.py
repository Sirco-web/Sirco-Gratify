#!/usr/bin/env python3
"""Training script for Gratify LLM with GPU support and checkpointing."""

import os
import sys
import json
import argparse
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from gpu_utils import setup_gpu_if_available, get_device_string, detect_gpu
from config import (
    GratifyConfig, SystemConfig, SYSTEM_BRAND, 
    DATA_DIR, CHECKPOINTS_DIR, get_checkpoint_path, 
    increment_checkpoint_version, get_latest_checkpoint
)
from model import GratifyLLM


class TextDataset(Dataset):
    """Dataset for text files."""
    
    def __init__(self, file_path=None, seq_length=512, tokenizer_fn=None, text=None):
        """Load text file and prepare data."""
        if text is None:
            with open(file_path, "r", encoding="utf-8") as f:
                self.text = f.read()
        else:
            self.text = text
        
        self.seq_length = seq_length
        self.tokenizer_fn = tokenizer_fn or self.char_tokenize
        self.tokens = self.tokenizer_fn(self.text)
    
    def char_tokenize(self, text):
        """Simple character-level tokenization."""
        chars = sorted(set(text))
        char_to_idx = {c: i for i, c in enumerate(chars)}
        return [char_to_idx[c] for c in text]
    
    def __len__(self):
        """Return number of sequences."""
        return max(0, len(self.tokens) - self.seq_length)
    
    def __getitem__(self, idx):
        """Get a sequence."""
        tokens = self.tokens[idx : idx + self.seq_length + 1]
        input_ids = torch.tensor(tokens[:-1], dtype=torch.long)
        target_ids = torch.tensor(tokens[1:], dtype=torch.long)
        return input_ids, target_ids


class Trainer:
    """Trainer class for Gratify LLM."""
    
    def __init__(self, model, config, device):
        """Initialize trainer."""
        self.model = model.to(device)
        self.config = config
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        self.global_step = 0
        self.best_loss = float("inf")
        
        # Load latest checkpoint if exists
        self.load_checkpoint()
    
    def train_step(self, batch):
        """Single training step."""
        input_ids, target_ids = batch
        input_ids = input_ids.to(self.device)
        target_ids = target_ids.to(self.device)
        
        # Forward pass
        logits = self.model(input_ids)
        loss = self.criterion(
            logits.view(-1, self.config.vocab_size),
            target_ids.view(-1)
        )
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
        self.optimizer.step()
        
        self.global_step += 1
        return loss.item()
    
    @torch.no_grad()
    def eval_step(self, dataloader):
        """Evaluate on validation set."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        for input_ids, target_ids in dataloader:
            input_ids = input_ids.to(self.device)
            target_ids = target_ids.to(self.device)
            
            logits = self.model(input_ids)
            loss = self.criterion(
                logits.view(-1, self.config.vocab_size),
                target_ids.view(-1)
            )
            total_loss += loss.item()
            num_batches += 1
        
        self.model.train()
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    def save_checkpoint(self, version=None):
        """Save model checkpoint."""
        if version is None:
            version = increment_checkpoint_version()
        
        checkpoint_path = get_checkpoint_path(version)
        
        checkpoint = {
            "version": version,
            "model_state": self.model.state_dict(),
            "optimizer_state": self.optimizer.state_dict(),
            "global_step": self.global_step,
            "config": self.config.__dict__,
            "brand": SYSTEM_BRAND,
        }
        
        torch.save(checkpoint, checkpoint_path)
        print(f"✅ Checkpoint v{version} saved to {checkpoint_path}")
        
        # Also save as latest
        torch.save(checkpoint, CHECKPOINTS_DIR / "latest_model.pt")
        
        return checkpoint_path
    
    def load_checkpoint(self, checkpoint_path=None):
        """Load model checkpoint."""
        if checkpoint_path is None:
            checkpoint_path = get_latest_checkpoint()
        
        if checkpoint_path is None or not checkpoint_path.exists():
            print("ℹ️  No checkpoint found. Starting fresh training.")
            return
        
        print(f"📂 Loading checkpoint from {checkpoint_path}...")
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint["model_state"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state"])
        self.global_step = checkpoint.get("global_step", 0)
        
        print(f"✅ Checkpoint loaded. Resuming from step {self.global_step}")


def load_training_data(data_dir):
    """Load training text from a directory.

    Supported file types:
    - .md: markdown/plain text
    - .txt: plain text
    - .jsonl: instruction/chat records (one JSON object per line)
    """

    def format_jsonl_record(obj: dict) -> str:
        # Common formats:
        # - {"text": "..."}
        # - {"prompt": "...", "completion": "..."}
        # - {"messages": [{"role":"system|user|assistant","content":"..."}]}
        if isinstance(obj.get("text"), str):
            return obj["text"].strip()

        if isinstance(obj.get("prompt"), str) or isinstance(obj.get("completion"), str):
            prompt = (obj.get("prompt") or "").strip()
            completion = (obj.get("completion") or "").strip()
            if prompt and completion:
                return f"User: {prompt}\nAssistant: {completion}".strip()
            return (prompt or completion).strip()

        msgs = obj.get("messages")
        if isinstance(msgs, list):
            out_lines: list[str] = []
            for m in msgs:
                if not isinstance(m, dict):
                    continue
                role = (m.get("role") or "").strip().lower()
                content = m.get("content")
                if not isinstance(content, str):
                    continue
                content = content.strip()
                if not content:
                    continue
                if role in {"system"}:
                    out_lines.append(f"System: {content}")
                elif role in {"user"}:
                    out_lines.append(f"User: {content}")
                elif role in {"assistant", "bot"}:
                    out_lines.append(f"Assistant: {content}")
                else:
                    out_lines.append(content)
            return "\n".join(out_lines).strip()

        # Fallback: stringify unknown objects (but keep it stable).
        return json.dumps(obj, ensure_ascii=False)

    base = Path(data_dir)
    md_folder = base / "md"  # prefer data/md/
    source_dir = md_folder if md_folder.exists() else base

    md_files = sorted(source_dir.glob("*.md"))
    txt_files = sorted(source_dir.glob("*.txt"))
    jsonl_files = sorted(source_dir.glob("*.jsonl"))

    total_files = len(md_files) + len(txt_files) + len(jsonl_files)
    if total_files == 0:
        print(f"⚠️  No .md/.txt/.jsonl files found in {source_dir}")
        print("   Add training files, then rerun training.")
        return None

    print(f"📂 Found {total_files} training files in {source_dir}")

    chunks: list[str] = []

    for p in md_files + txt_files:
        print(f"   - {p.name}")
        with open(p, "r", encoding="utf-8") as f:
            chunks.append(f.read().strip())

    for p in jsonl_files:
        print(f"   - {p.name}")
        num_records = 0
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(obj, dict):
                    continue
                formatted = format_jsonl_record(obj)
                if formatted:
                    chunks.append(formatted)
                    num_records += 1
        print(f"     records: {num_records}")

    # Separate docs/conversations so the model learns boundaries.
    return "\n\n---\n\n".join([c for c in chunks if c])


def setup_training(args):
    """Setup training environment."""
    print("🚀 Starting Gratify Training Setup...")
    print(f"   Version: {SYSTEM_BRAND['version']}")
    print(f"   Author: {SYSTEM_BRAND['author']}")
    
    # GPU setup
    print("\n🔧 Checking GPU support...")
    # Training must NOT install or modify dependencies (including GPU/CUDA).
    gpu_available = setup_gpu_if_available(install=False)
    device = torch.device(get_device_string())
    print(f"📍 Using device: {device}")
    
    # Config
    config = GratifyConfig.load() if args.resume else GratifyConfig()
    system_config = SystemConfig()
    system_config.device = device
    
    # Data
    print("\n📚 Loading training data...")
    training_text = load_training_data(DATA_DIR)
    if training_text is None:
        print("\n✋ Training aborted: No training data found.")
        return None
    
    # Create dataset
    dataset = TextDataset(
        seq_length=config.max_seq_length,
        text=training_text
    )
    
    # Update vocab size based on actual characters
    unique_tokens = len(set(dataset.tokens))
    config.vocab_size = unique_tokens
    print(f"   Vocabulary size: {config.vocab_size}")
    print(f"   Total tokens: {len(dataset.tokens):,}")
    
    # Model
    print("\n🧠 Creating model...")
    model = GratifyLLM(config)
    param_count = model.count_parameters()
    print(f"   Parameters: {param_count:,}")
    
    # Trainer
    trainer = Trainer(model, config, device)
    
    # DataLoader
    train_loader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0,  # 0 for compatibility
    )
    
    return {
        "config": config,
        "system_config": system_config,
        "model": model,
        "trainer": trainer,
        "train_loader": train_loader,
        "dataset": dataset,
    }


def train(setup_dict, epochs=None, save_interval=500):
    """Training loop."""
    config = setup_dict["config"]
    trainer = setup_dict["trainer"]
    train_loader = setup_dict["train_loader"]
    epochs = epochs or config.num_epochs
    
    print(f"\n{'='*60}")
    print(f"🎓 Starting Training ({SYSTEM_BRAND['name']})")
    print(f"{'='*60}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {config.batch_size}")
    print(f"Learning rate: {config.learning_rate}")
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
            
            # Save checkpoint
            if trainer.global_step % save_interval == 0:
                trainer.save_checkpoint()
        
        epoch_avg_loss = epoch_loss / num_batches
        print(f"\n✅ Epoch {epoch+1}/{epochs} completed. Avg Loss: {epoch_avg_loss:.4f}\n")
    
    # Final checkpoint
    trainer.save_checkpoint()
    print(f"\n{'='*60}")
    print(f"🎉 Training completed!")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Train Gratify LLM from scratch"
    )
    parser.add_argument(
        "--epochs", type=int, default=None,
        help="Number of training epochs (default: from config)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=None,
        help="Batch size (default: from config)"
    )
    parser.add_argument(
        "--lr", type=float, default=None,
        help="Learning rate (default: from config)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from latest checkpoint"
    )
    parser.add_argument(
        "--save-config", action="store_true",
        help="Save config after setup"
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_result = setup_training(args)
    if setup_result is None:
        sys.exit(1)
    
    # Override config if specified
    if args.batch_size:
        setup_result["config"].batch_size = args.batch_size
    if args.lr:
        setup_result["config"].learning_rate = args.lr
    
    # Save config if requested
    if args.save_config:
        setup_result["config"].save()
    
    # Train
    train(setup_result, epochs=args.epochs)


if __name__ == "__main__":
    main()
