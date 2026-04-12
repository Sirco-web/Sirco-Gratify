# LLM Training from Scratch 🚀

A complete end-to-end framework for training Large Language Models from the ground up. This repository provides everything needed to build, train, and deploy a transformer-based LLM.

## 🎯 Features

- **Modern LLM Architecture**: Transformer-based model with RoPE positional embeddings
- **Efficient Training**: Mixed precision training, gradient accumulation, checkpointing
- **Data Pipeline**: Complete data preparation from raw text to tokenized datasets
- **Advanced Techniques**:
  - Tensor Parallelism support
  - KV-cache for efficient generation
  - SentencePiece tokenization (LLaMA style)
  - Learning rate warmup and scheduling
- **Multi-Mode**: Train, evaluate, generate, or interactive chat

## 📋 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# For GPU support, ensure PyTorch CUDA is installed
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Prepare Data

```bash
# Download and preprocess training data
python data_prep.py

# This will:
# - Download sample datasets (WikiText, Books)
# - Combine and clean the text
# - Split into train/val/test sets
# - Output to data/processed/
```

### 3. Train Tokenizer

```bash
# Train SentencePiece tokenizer on your data
python setup_tokenizer.py

# Creates: tokenizers/tokenizer.model
```

### 4. Train the Model

```bash
# Start training with default config
python run_training.py --mode train

# With custom config
python run_training.py --mode train \
  --batch_size 64 \
  --seq_len 512 \
  --dim 512 \
  --layers 12 \
  --epochs 20
```

### 5. Generate Text

```bash
# Generate from a prompt
python run_training.py --mode generate \
  --prompt "Artificial intelligence" \
  --max_tokens 200

# Interactive chat mode
python run_training.py --mode chat
```

## 📁 Project Structure

```
.
├── train.py                 # Core model and training functions
├── dataset.py              # Dataset classes for data loading
├── data_prep.py            # Data download and preprocessing
├── setup_tokenizer.py      # Tokenizer training and setup
├── run_training.py         # Main training orchestrator
├── requirements.txt        # Python dependencies
│
├── data/                   # Training data
│   ├── raw/               # Downloaded raw text files
│   └── processed/         # Tokenized datasets
│       ├── train.txt
│       ├── val.txt
│       └── test.txt
│
├── tokenizers/            # Trained tokenizers
│   └── tokenizer.model
│
└── checkpoints/           # Model checkpoints
    ├── model_step_1000.pt
    └── model_step_2000.pt
```

## 🏗️ Architecture

### Model Configuration

```python
Config:
  dim = 256          # Hidden dimension
  heads = 8          # Attention heads
  layers = 6         # Transformer layers
  seq_len = 256      # Sequence length
  vocab_size = 32000 # SentencePiece vocab size
```

### Key Components

1. **Tokenization**: SentencePiece (BPE subword tokenization)
2. **Embeddings**: Learned token embeddings + RoPE positional encodings
3. **Attention**: Multi-head scaled dot-product with causal masking
4. **Feed-Forward**: 4x hidden dimension with SiLU activation
5. **Normalization**: Pre-norm with LayerNorm
6. **Optimization**: AdamW with warmup scheduling

### Generation Methods

- **Greedy Decoding**: Always pick the most likely next token
- **Sampling**: Sample from the probability distribution
- **Temperature Scaling**: Control output diversity
- **KV-Cache**: Efficient generation with cached attention states

## 🔧 Configuration

Edit `train.py` Config class to customize:

```python
class Config:
    dim = 256              # Model hidden dimension
    heads = 8              # Attention heads
    layers = 6             # Number of transformer blocks
    seq_len = 256          # Maximum context length
    vocab_size = 32000     # Tokenizer vocabulary size
    
    lr = 3e-4              # Learning rate
    batch_size = 32        # Training batch size
    num_epochs = 10        # Number of training epochs
    warmup_steps = 1000    # Warmup steps
    max_steps = 100000     # Maximum training steps
    save_interval = 1000   # Save checkpoint every N steps
```

## 📊 Training

### Starting Training

```bash
python run_training.py --mode train
```

**What happens:**
1. Loads tokenizer from `tokenizers/tokenizer.model`
2. Creates datasets from `data/processed/`
3. Initializes model with config from train.py
4. Trains with mixed precision (if GPU available)
5. Saves checkpoints every 1000 steps
6. Validates on validation set

### Monitoring

Training output shows:
- Loss at regular intervals
- Validation loss
- Learning rate schedule
- Checkpoint locations

### Checkpointing

Checkpoints include:
- Model weights
- Optimizer state (for resuming)
- Training step count
- Configuration used

**Resume from checkpoint:**
```python
checkpoint = torch.load("checkpoints/model_step_5000.pt")
model.load_state_dict(checkpoint['model'])
optimizer.load_state_dict(checkpoint['optimizer'])
```

## 🧠 Model Usage

### Text Generation

```python
from train import Config, LLM, generate
from setup_tokenizer import TokenizerManager

cfg = Config()
model = LLM(cfg).cuda()

# Load trained model
checkpoint = torch.load("checkpoints/model_step_10000.pt")
model.load_state_dict(checkpoint['model'])

# Setup tokenizer
mgr = TokenizerManager()
tokenizer = mgr.load_tokenizer("tokenizers/tokenizer.model")

# Generate text
output = generate(model, tokenizer, "Hello world", max_new_tokens=100)
print(output)
```

### Fine-tuning

```python
# Load pretrained model
model = LLM(cfg)
model.load_state_dict(torch.load("model.pt"))

# Fine-tune on new data
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)

for x, y in finetune_dataloader:
    logits = model(x)
    loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))
    loss.backward()
    optimizer.step()
```

### Inference Optimization

**KV-Cache for faster generation:**
```python
# During training (prefill):
logits = model(x)

# During generation (use cache):
cache = KVCache(cfg.layers, cfg.heads, cfg.dim // cfg.heads)
logits = model(x, cache=cache, use_cache=True)
```

## 🚀 Advanced Usage

### Custom Data Source

Add your own data source in `data_prep.py`:

```python
def download_custom_data(self):
    """Download from custom source"""
    # Your implementation here
    return file_paths
```

### Custom Model Architecture

Modify network in `train.py`:

```python
class Block(nn.Module):
    def __init__(self, cfg, i):
        super().__init__()
        # Your custom layers
```

### Distributed Training

Enable tensor parallelism:

```python
cfg.tp_size = torch.cuda.device_count()  # Use all GPUs
```

## 📈 Performance Tips

1. **Increase batch size** for better GPU utilization (if memory allows)
2. **Longer sequences** = more context but slower training
3. **More layers** = better capacity but slower training
4. **Warmup steps** improve stability with high learning rates
5. **Gradient accumulation** simulates larger batches

## 🐛 Troubleshooting

### Out of Memory (OOM)

```bash
# Reduce batch size
python run_training.py --batch_size 16

# Reduce sequence length
python run_training.py --seq_len 128

# Reduce model size
python run_training.py --dim 128 --layers 3
```

### Slow Data Loading

- Pre-compute tokenization: `dataset.py` handles caching
- Increase `num_workers` in `create_dataloader()`
- Use faster storage (SSD)

### Training Divergence

- Reduce learning rate: `--lr 1e-4`
- Increase warmup steps: adjust in `train.py`
- Check gradient norms during training

### No GPU Available

```bash
# Training will automatically use CPU
python run_training.py --device cpu
```

## 📚 References

- Attention Is All You Need (Vaswani et al., 2017)
- RoFormer: Enhanced Transformer with Rotary Position Embedding (Su et al., 2021)
- LLaMA: Open and Efficient Foundation Language Models (Touvron et al., 2023)
- Efficient Transformers: A Survey (Tay et al., 2022)

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Distributed training (DDP)
- [ ] Mixed precision optimization
- [ ] Custom attention kernels
- [ ] Model quantization
- [ ] Knowledge distillation
- [ ] Inference API server

## 📞 Support

For issues or questions:

1. Check troubleshooting section above
2. Review training logs in `checkpoints/`
3. Check data files exist in `data/processed/`
4. Ensure tokenizer trained in `tokenizers/`

---

**Happy Training! 🎉**

Built with PyTorch 🔥
