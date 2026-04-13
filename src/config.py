"""Configuration for Gratify LLM trainer."""

import os
import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
USER_DATA_DIR = PROJECT_ROOT / "user_data"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
CONFIG_FILE = PROJECT_ROOT / "config.json"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
USER_DATA_DIR.mkdir(exist_ok=True)
CHECKPOINTS_DIR.mkdir(exist_ok=True)

# Model configuration
class GratifyConfig:
    """Default configuration for Gratify LLM."""
    
    # Model architecture
    vocab_size = 10000
    max_seq_length = 512
    embedding_dim = 256
    num_layers = 4
    num_heads = 8
    hidden_dim = 512
    dropout = 0.1
    
    # Training
    batch_size = 16
    learning_rate = 1e-3
    num_epochs = 10
    warmup_steps = 500
    max_grad_norm = 1.0
    
    # Checkpointing
    save_every_n_steps = 500
    eval_every_n_steps = 1000
    
    # Data
    data_split = {"train": 0.8, "val": 0.1, "test": 0.1}
    tokenizer_type = "char"  # or 'bpe' later
    
    @classmethod
    def from_dict(cls, config_dict):
        """Create config from dictionary."""
        config = cls()
        for key, value in config_dict.items():
            setattr(config, key, value)
        return config
    
    @classmethod
    def load(cls):
        """Load config from file or use defaults."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        return cls()
    
    def save(self):
        """Save config to file."""
        config_dict = self.__dict__
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_dict, f, indent=4)
        print(f"✅ Config saved to {CONFIG_FILE}")


# System config
class SystemConfig:
    """System-level configuration."""
    
    device = None  # Will be set based on GPU detection
    use_mixed_precision = False
    seed = 42
    num_workers = 4
    pin_memory = True
    
    # Logging
    log_dir = PROJECT_ROOT / "logs"
    log_level = "INFO"
    
    # Checkpointing
    best_checkpoint = CHECKPOINTS_DIR / "best_model.pt"
    latest_checkpoint = CHECKPOINTS_DIR / "latest_model.pt"
    
    def __init__(self):
        self.log_dir.mkdir(exist_ok=True)


# System brand config
SYSTEM_BRAND = {
    "name": "Gratify",
    "author": "sirco",
    "version": "0.1.0",
}

def get_checkpoint_path(version=None):
    """Get checkpoint path with optional version number."""
    if version is None:
        # Get latest version
        existing = list(CHECKPOINTS_DIR.glob("checkpoint_v*.pt"))
        if existing:
            versions = [int(f.stem.split("_v")[-1]) for f in existing]
            version = max(versions) + 1
        else:
            version = 1
    return CHECKPOINTS_DIR / f"checkpoint_v{version}.pt"


def get_latest_checkpoint():
    """Get the latest checkpoint path."""
    checkpoints = list(CHECKPOINTS_DIR.glob("checkpoint_v*.pt"))
    if checkpoints:
        versions = [(int(f.stem.split("_v")[-1]), f) for f in checkpoints]
        return max(versions, key=lambda x: x[0])[1]
    return None


def increment_checkpoint_version():
    """Get next checkpoint version number."""
    existing = list(CHECKPOINTS_DIR.glob("checkpoint_v*.pt"))
    if existing:
        versions = [int(f.stem.split("_v")[-1]) for f in existing]
        return max(versions) + 1
    return 1
