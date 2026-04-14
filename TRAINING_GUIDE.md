# Gratify LLM 🤖

**An LLM you can train from scratch with automatic GPU support and checkpoint versioning.**

A lightweight language model training framework built by **Sirco** that emphasizes simplicity, efficiency, and ease of use.

## Quick Start

### 1. Setup

```bash
python setup.py
```

The setup script will:
- ✅ Create the necessary directories
- ✅ Install dependencies  
- ✅ Auto-detect GPU hardware
- ✅ Install GPU-specific libraries if available
- ✅ Create sample training data

### 2. Add Training Data

Add markdown (`.md`) files to the `data/` directory:

```bash
ls data/
# sample.md
# my_training_data.md
# more_data.md
```

The more data, the better the model!

You can also add:
- `.txt` plain text files
- `.jsonl` chat/instruction data (recommended for better chat behavior)

### 3. Train the Model

```bash
python src/train.py
```

Start training from scratch. The script will:
- 🔍 Auto-detect GPU and enable if available
- 📊 Show training progress
- 💾 Save checkpoints with version numbers
- 📈 Display loss metrics

**Options:**
```bash
python src/train.py --epochs 20 --batch-size 32 --lr 0.001
python src/train.py --resume  # Continue from latest checkpoint
python src/train.py --save-config  # Save configuration
```

### 4. Chat with Your Model

```bash
python src/cli.py
```

Interact with your trained model:

```
You: what are you ai
Bot: I am Gratify by sirco

You: /about
Bot: [Shows model information]

You: /help
Bot: [Shows available commands]
```

## Project Structure

```
Sirco-Gratify/
├── data/                    # 📚 Training data (.md files)
│   └── sample.md
├── user_data/               # 👤 User interactions & chat history
│   └── chat_history.json
├── checkpoints/             # 💾 Model checkpoints with versions
│   ├── checkpoint_v1.pt
│   ├── checkpoint_v2.pt
│   └── latest_model.pt
├── src/
│   ├── __init__.py
│   ├── gpu_utils.py        # 🔧 GPU detection & setup
│   ├── config.py           # ⚙️ Configuration management
│   ├── model.py            # 🧠 Model architecture
│   ├── train.py            # 📖 Training script
│   └── cli.py              # 💬 Chat interface
├── requirements.txt         # 📦 Dependencies
├── setup.py                # 🚀 Setup script
└── README.md
```

## GPU Support

Gratify automatically detects and utilizes available GPUs:

### NVIDIA CUDA
- **Automatic Detection**: ✅ Yes
- **Install**: CUDA Toolkit required
- **Speed**: ~10-50x faster than CPU

```bash
# Setup script will install CUDA PyTorch automatically
```

### AMD ROCm
- **Automatic Detection**: ✅ Yes  
- **Install**: ROCm runtime required
- **Speed**: ~10-30x faster than CPU

### Apple Metal (Apple Silicon)
- **Automatic Detection**: ✅ Yes
- **Install**: Automatic with M1/M2/M3 Macs
- **Speed**: ~5-20x faster than CPU

### CPU Only
- **Fallback**: ✅ Yes
- **No setup needed**: Just works
- **Note**: Slower but compatible with all systems

## Features

### 🧠 Model Architecture
- Transformer-based LLM
- Configurable layers, heads, and dimensions
- Multi-head self-attention
- Positional encoding
- Residual connections
- Layer normalization

### 💾 Checkpoint System
- **Automatic Versioning**: `checkpoint_v1.pt`, `checkpoint_v2.pt`, etc.
- **Version Tracking**: Each checkpoint stores metadata
- **Resume Training**: Continue from any checkpoint
- **Latest Pointer**: `latest_model.pt` always points to most recent

### 🔧 GPU Acceleration
```python
# Automatically detected at startup
# Support for NVIDIA (CUDA), AMD (ROCm), Apple (Metal)
# Falls back to CPU gracefully
```

### 📊 Training Features
- Character-level tokenization
- Configurable training parameters
- Progress tracking
- Loss monitoring
- Batch processing

### 💬 CLI Chat Interface
- Interactive conversation
- Chat history saved to `user_data/`
- Built-in responses (e.g., "I am Gratify by sirco")
- Commands for model info and configuration
- Temperature control for generation

## Configuration

Edit training parameters in `config.py` or via CLI:

```python
# Model
vocab_size = 10000
embedding_dim = 256
num_layers = 4
num_heads = 8

# Training
batch_size = 16
learning_rate = 1e-3
num_epochs = 10
max_grad_norm = 1.0
```

Or override via command line:

```bash
python src/train.py --batch-size 32 --lr 0.0005 --epochs 50
```

## CLI Commands

When chatting with the model:

```
/quit or /exit       - Exit chat
/clear               - Clear chat history
/history             - Show conversation history
/about               - Show model information
/set temp 0.8        - Set temperature (0.0-1.0)
/set tokens 100      - Set max response tokens
```

## Example Workflow

```bash
# 1. Setup
python setup.py

# 2. Check GPU
python -c "from src.gpu_utils import detect_gpu; import json; print(json.dumps(detect_gpu(), indent=2))"

# 3. Add your training data to data/ folder

# 4. Train
python src/train.py --epochs 5

# 5. Resume training later
python src/train.py --resume --epochs 10

# 6. Chat
python src/cli.py
```

## Performance Notes

### Training Speed
- **GPU**: 50-200 samples/sec (CUDA) / 30-100 samples/sec (Apple Metal)
- **CPU**: 5-20 samples/sec

### Checkpoint Size
- **Model**: ~50-100 MB depending on vocabulary and layers
- **Full Checkpoint**: +metadata ~50-110 MB per version

### Memory Usage
- **GPU VRAM**: 2-8 GB (configurable via batch_size)
- **CPU RAM**: 4-16 GB recommended

## Troubleshooting

### No GPU detected even though I have one
1. Check installation: `python -m pip list | grep torch`
2. Verify GPU drivers are installed
3. Run setup again: `python setup.py`

### Out of memory during training
- Reduce batch size: `python src/train.py --batch-size 8`
- Reduce max sequence length in config
- Use CPU if GPU memory is limited

### Model seems to be repeating
- Increase training data
- Train for more epochs
- Increase model size (embedding_dim, layers)

### Chat not responding
- Ensure model is trained: `ls checkpoints/`
- Check GPU/CPU availability
- Verify data was used for training

## Extensions

### Add custom tokenizers
Edit `config.py` tokenizer_type and implement in training script

### Multi-GPU training
Modify `train.py` to use `torch.nn.DataParallel`

### Model quantization
Use `torch.quantization` for CPU optimization

### Fine-tuning
Load checkpoint and train with new data

### JSONL chat data (recommended)
Put `.jsonl` files in `data/finetune/` (or `data/md/` if you want them in full training).
Each line should be a JSON object in one of these formats:

```json
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}]}
```

or:

```json
{"prompt":"...","completion":"..."}
```

## Model Capabilities

- **Generate text** from prompts
- **Learn patterns** from training data
- **Adapt** to any domain via training data
- **Run on edge devices** with CPU fallback

## Requirements

- Python 3.8+
- PyTorch 2.0+
- NumPy
- CUDA/ROCm/Metal (optional, auto-detected)

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 8+ cores |
| RAM | 4 GB | 16 GB+ |
| GPU VRAM | - | 4 GB+ |
| Storage | 5 GB | 20 GB+ |
| OS | Linux/Mac/Windows | Linux recommended |

## License

Open source - Feel free to use, modify, and distribute

## Author

**Sirco** - AI/ML Framework Designer

## Contributing

Contributions welcome! Areas for improvement:
- Better tokenizers (BPE, WordPiece)
- Distributed training
- Quantization support
- Web UI for chat
- Model deployment optimizations

## Citation

If you use Gratify in your work:

```
Gratify LLM
Author: Sirco
Year: 2026
```

---

**Happy Training! 🚀** Start with small models and data, scale up as you learn the framework.
