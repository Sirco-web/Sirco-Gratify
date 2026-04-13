# Gratify LLM 🤖

**A complete language model training framework you can build and train from scratch.**

An LLM training system with:
- ✅ **2 Data Folders**: `data/` for training files, `user_data/` for user interactions
- ✅ **GPU Auto-Detection**: Automatically detects and uses NVIDIA CUDA, AMD ROCm, or Apple Metal
- ✅ **Checkpoint System**: Version-numbered checkpoints (`checkpoint_v1.pt`, `checkpoint_v2.pt`, etc.)
- ✅ **Simple CLI**: Interactive chat interface with the model
- ✅ **Built-in Response**: "What are you ai?" → "I am Gratify by sirco"

## 🚀 Quick Start

```bash
# 1. One-command setup (detects GPU automatically)
python setup.py

# 2. Add markdown files to data/
# (setup.py creates sample.md to get you started)

# 3. Train the model with GPU acceleration if available
python src/train.py

# 4. Chat with your model
python src/cli.py
```

## 📁 Project Structure

```
Sirco-Gratify/
│
├── data/                    # 📚 Training data (add .md files here)
│   └── sample.md
│
├── user_data/               # 👤 User data & chat history
│   └── chat_history.json
│
├── checkpoints/             # 💾 Versioned model checkpoints
│   ├── checkpoint_v1.pt     # First training
│   ├── checkpoint_v2.pt     # Continued training
│   └── latest_model.pt      # Always points to latest
│
├── src/                     # 🔧 Source code
│   ├── train.py            # Training script (GPU-enabled)
│   ├── cli.py              # Chat interface
│   ├── model.py            # Transformer model
│   ├── config.py           # Configuration
│   └── gpu_utils.py        # GPU detection & setup
│
├── setup.py                # 🚀 Setup script
├── requirements.txt        # 📦 Dependencies
├── TRAINING_GUIDE.md       # 📖 Detailed guide
└── README.md
```

## 🔧 GPU Support

Automatic GPU detection for:
- 🟢 **NVIDIA CUDA** - Fastest on NVIDIA GPUs
- 🟠 **AMD ROCm** - For AMD GPUs
- 🍎 **Apple Metal** - Native on Apple Silicon (M1/M2/M3)
- ⚪ **CPU** - Works everywhere as fallback

When you run training or CLI, the system automatically:
1. Detects available GPU hardware
2. Installs appropriate libraries
3. Configures PyTorch for that device
4. Uses it at full power for training

```bash
$ python src/train.py
🔧 Checking GPU support...
✨ GPU DETECTED: CUDA
   Devices: 1
   Compute Capability: (8, 6)
Installing CUDA-enabled PyTorch...
✅ CUDA dependencies installed!
```

## 💬 Built-in Interactions

The CLI has a built-in response:

```
You: what are you ai
Bot: I am Gratify by sirco
```

Plus many other helpful commands and responses!

## 📊 Checkpoint & Versioning System

Each training session creates numbered checkpoints:

```
checkpoints/
├── checkpoint_v1.pt      # Initial training
├── checkpoint_v2.pt      # Continued training  
├── checkpoint_v3.pt      # Another session
└── latest_model.pt       # Symlink to v3
```

Resume from any checkpoint:
```bash
python src/train.py --resume    # Continues from latest
```

## 🎯 Key Features

| Feature | Details |
|---------|---------|
| **Training** | Character-level tokenization, configurable architecture |
| **History** | Chat history automatically saved in `user_data/` |
| **Speed** | 10-50x faster with GPU (CUDA), 5-20x with Apple Metal |
| **Simplicity** | No complex setup, auto-detection handles everything |
| **Scalability** | Train small or large models based on your data |
| **Portability** | Same code works on Linux, Mac, Windows |

## 📚 Full Guide

For detailed information on:
- Training configuration
- CLI commands
- Performance optimization
- Troubleshooting

See [TRAINING_GUIDE.md](TRAINING_GUIDE.md)

## 📖 Training Data

Add markdown files (`.md`) to the `data/` directory:

```bash
data/
├── sample.md           # Created by setup
├── my_book.md          # Your training data
├── documentation.md    # More examples
└── ...                 # Add as many as you want
```

The model learns from all text in these files!

## 💻 Example Workflow

```bash
# Setup everything
python setup.py

# Check what GPU we have (if any)
python -c "from src.gpu_utils import detect_gpu; print(detect_gpu())"

# Train for 5 epochs on your data
python src/train.py --epochs 5

# Verify checkpoint was created
ls -lh checkpoints/

# Chat with the model
python src/cli.py

# Later: continue training with more data
python src/train.py --resume --epochs 10

# Chat again - model is better!
python src/cli.py
```

## 🖥️ Minimum Requirements

- Python 3.8+
- 4 GB RAM (CPU mode) or 2GB VRAM (GPU)
- 5 GB disk space

For GPU acceleration, install appropriate drivers:
- **NVIDIA**: CUDA Toolkit (auto-installed)
- **AMD**: ROCm (auto-installed)  
- **Apple**: Built-in on Apple Silicon

## 🌟 What You Can Do

1. **Train a custom LLM** - Any domain by changing training data
2. **Generate text** - From any prompt
3. **Continue training** - Add new data, keep improving model
4. **Experiment** - Change model size, training parameters
5. **Deploy** - Use the checkpoint on any machine with Python

## 📝 Commands Reference

### Training
```bash
python src/train.py                    # Train from scratch
python src/train.py --resume           # Continue from checkpoint
python src/train.py --epochs 20        # Set epochs
python src/train.py --batch-size 32    # Set batch size
python src/train.py --lr 0.001         # Set learning rate
```

### Chat
```bash
python src/cli.py                      # Start chatting

# In chat, use commands:
/quit                    # Exit
/about                   # Model info
/history                 # Show past conversations
/set temp 0.8            # Temperature (creativity)
/set tokens 100          # Max tokens to generate
```

## ❓ FAQ

**Q: How much training data do I need?**
A: Start with 1-10 MB of text. More data = better model. Even a few books work!

**Q: Will it use my GPU automatically?**
A: Yes! Just run setup.py and it detects everything.

**Q: Can I use it on CPU only?**
A: Yes, it works everywhere. GPU just makes it faster.

**Q: How do I add new training data?**
A: Put `.md` files in `data/` and run `python src/train.py --resume`

**Q: Where is the chat history saved?**
A: In `user_data/chat_history.json`

**Q: Can I share the trained model?**
A: Yes! Just copy the checkpoint file from `checkpoints/`

## 🔗 Important Files

- [TRAINING_GUIDE.md](TRAINING_GUIDE.md) - Complete documentation
- [src/model.py](src/model.py) - Model architecture
- [src/config.py](src/config.py) - Configuration options
- [src/gpu_utils.py](src/gpu_utils.py) - GPU detection

## 🎉 Getting Started Now

```bash
# This is all you need:
python setup.py
python src/train.py
python src/cli.py
```

---

**Built by Sirco** - An LLM framework for everyone

Made to be simple, powerful, and automatic. 🚀
