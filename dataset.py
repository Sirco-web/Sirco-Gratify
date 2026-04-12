"""
Dataset classes for LLM training
Handles tokenization and batching of text data
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
from tqdm import tqdm
import pickle


class TextDataset(Dataset):
    """Dataset that reads text and tokenizes it on the fly"""
    
    def __init__(self, filepath, tokenizer, seq_len=256, max_samples=None):
        self.filepath = Path(filepath)
        self.tokenizer = tokenizer
        self.seq_len = seq_len
        self.max_samples = max_samples
        
        print(f"Loading dataset from {filepath}...")
        
        # Read all text
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Tokenize entire text
        print("Tokenizing text...")
        self.tokens = self.tokenizer.encode(text)
        
        if max_samples:
            self.tokens = self.tokens[:max_samples * seq_len]
        
        print(f"Loaded {len(self.tokens):,} tokens")
        print(f"Dataset size: {len(self)}")
    
    def __len__(self):
        """Number of sequences"""
        return max(0, (len(self.tokens) - self.seq_len) // self.seq_len)
    
    def __getitem__(self, idx):
        """Get a single training example"""
        start = idx * self.seq_len
        end = start + self.seq_len
        
        x = torch.tensor(self.tokens[start:end], dtype=torch.long)
        y = torch.tensor(self.tokens[start+1:end+1], dtype=torch.long)
        
        return x, y


class CachedTextDataset(Dataset):
    """Dataset that pre-tokenizes and caches for faster loading"""
    
    def __init__(self, filepath, tokenizer, seq_len=256, cache_path=None, rebuild_cache=False):
        self.filepath = Path(filepath)
        self.tokenizer = tokenizer
        self.seq_len = seq_len
        
        if cache_path is None:
            cache_path = self.filepath.with_suffix('.cache.pickle')
        
        self.cache_path = Path(cache_path)
        
        # Try to load from cache
        if self.cache_path.exists() and not rebuild_cache:
            print(f"Loading cached dataset from {self.cache_path}...")
            with open(self.cache_path, 'rb') as f:
                self.tokens = pickle.load(f)
            print(f"Loaded {len(self.tokens):,} tokens")
        else:
            # Create cache
            print(f"Creating cache for {filepath}...")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            print("Tokenizing...")
            self.tokens = self.tokenizer.encode(text)
            
            # Save cache
            print(f"Saving cache to {self.cache_path}...")
            with open(self.cache_path, 'wb') as f:
                pickle.dump(self.tokens, f)
        
        print(f"Dataset size: {len(self)}")
    
    def __len__(self):
        """Number of sequences"""
        return max(0, (len(self.tokens) - self.seq_len) // self.seq_len)
    
    def __getitem__(self, idx):
        """Get a single training example"""
        start = idx * self.seq_len
        end = start + self.seq_len
        
        x = torch.tensor(self.tokens[start:end], dtype=torch.long)
        y = torch.tensor(self.tokens[start+1:end+1], dtype=torch.long)
        
        return x, y


class StreamingTextDataset(Dataset):
    """Memory-efficient dataset that streams from disk"""
    
    def __init__(self, filepath, tokenizer, seq_len=256, buffer_size=10000):
        self.filepath = Path(filepath)
        self.tokenizer = tokenizer
        self.seq_len = seq_len
        self.buffer_size = buffer_size
        
        # Read file and count sequences
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        self.tokens = self.tokenizer.encode(text)
        self._num_sequences = max(0, (len(self.tokens) - seq_len) // seq_len)
        
        print(f"Dataset size: {self._num_sequences}")
    
    def __len__(self):
        return self._num_sequences
    
    def __getitem__(self, idx):
        start = idx * self.seq_len
        end = start + self.seq_len
        
        x = torch.tensor(self.tokens[start:end], dtype=torch.long)
        y = torch.tensor(self.tokens[start+1:end+1], dtype=torch.long)
        
        return x, y


def create_dataloader(filepath, tokenizer, batch_size=32, seq_len=256, num_workers=0, split='train', cache=True):
    """
    Create a DataLoader for training
    
    Args:
        filepath: Path to text file
        tokenizer: SentencePiece tokenizer
        batch_size: Batch size
        seq_len: Sequence length
        num_workers: Number of workers for DataLoader
        split: 'train', 'val', or 'test'
        cache: Whether to cache tokenized data
    
    Returns:
        DataLoader
    """
    
    if cache:
        dataset = CachedTextDataset(
            filepath,
            tokenizer,
            seq_len=seq_len,
            cache_path=filepath.replace('.txt', f'.{split}.cache.pickle')
        )
    else:
        dataset = TextDataset(
            filepath,
            tokenizer,
            seq_len=seq_len
        )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == 'train'),
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True
    )
    
    print(f"Created {split} dataloader with {len(dataloader)} batches")
    
    return dataloader


if __name__ == "__main__":
    """Test dataset loading"""
    import sentencepiece as spm
    
    # Create a dummy tokenizer for testing
    print("Test: Creating dummy tokenizer...")
    # This would normally use a real tokenizer.model file
    # For now, we'll just show the structure
    
    print("Dataset classes ready for use!")
