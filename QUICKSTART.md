# Getting Started - Quick Reference

## 5-Minute Setup

```bash
# 1. Setup (auto-detects GPU, installs dependencies)
python setup.py

# 2. Verify everything works
python test_system.py

# 3. Check available data
ls data/

# 4. Done! Ready to use
```

## Training Your Model

### First Time Training
```bash
# Basic training
python src/train.py

# With custom settings
python src/train.py --epochs 20 --batch-size 32

# Save configuration
python src/train.py --save-config
```

### Continue Training
```bash
# Resume from latest checkpoint
python src/train.py --resume

# Continue with more epochs
python src/train.py --resume --epochs 50
```

### Advanced Training
```bash
# With all options
python src/train.py \
  --epochs 100 \
  --batch-size 16 \
  --lr 0.001 \
  --resume

# Force CPU training
CUDA_VISIBLE_DEVICES="" python src/train.py

# With Makefile (if installed)
make train
make resume
```

## Chatting with Your Model

### Basic Chat
```bash
# Start chat interface
python src/cli.py

# Examples:
You: hello
Bot: [generated response]

You: what are you ai
Bot: I am Gratify by sirco

You: /about
Bot: [shows model info]

You: /quit
Bot: Goodbye!
```

### Chat Commands
```
In chat, type:

/help or /about     - Show model information
/quit or /exit      - Exit chat
/clear              - Clear conversation history
/history            - Show past conversations
/set temp 0.5       - Set temperature (0-1)
/set tokens 100     - Set response length

Everything else is taken as a prompt to the model
```

### Custom Settings
```bash
# Higher temperature (more creative)
python src/cli.py --temp 0.9

# Lower temperature (more predictable)
python src/cli.py --temp 0.3

# Longer responses
python src/cli.py --max-tokens 200

# Use specific checkpoint
python src/cli.py --checkpoint checkpoints/checkpoint_v3.pt
```

## Managing Your Data

### Add Training Data
```bash
# Create markdown file
cat > data/mydata.md << 'EOF'
# My Training Data

This is content the model will learn from.

## Topics
- Item 1
- Item 2

More content here...
EOF

# Then retrain
python src/train.py --resume --epochs 10
```

### Check Data Size
```bash
# How much data do we have?
du -sh data/

# Count files
ls data/*.md | wc -l

# Show first lines
head -20 data/sample.md
```

## Monitoring Progress

### During Training
```
Epoch 1/20 | Batch 150/500 | Loss: 3.2451 | Step: 1500
Epoch 1/20 | Batch 160/500 | Loss: 3.1923 | Step: 1600
✅ Epoch 1/20 completed. Avg Loss: 3.2145

✅ Checkpoint v1 saved to checkpoints/checkpoint_v1.pt
```

### Check Checkpoints
```bash
# List all checkpoints
ls -lh checkpoints/

# Latest checkpoint
ls -lh checkpoints/checkpoint_v*.pt | tail -1

# Download/backup checkpoint
cp checkpoints/checkpoint_v5.pt my_model_backup.pt
```

## Troubleshooting

### "No checkpoints found!"
```bash
# Need to train first
python src/train.py

# With sample data
ls data/sample.md
```

### "Out of memory"
```bash
# Reduce batch size
python src/train.py --batch-size 8

# Use CPU instead
CUDA_VISIBLE_DEVICES="" python src/train.py
```

### "GPU not detected"
```bash
# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Rerun setup
python setup.py

# Then train
python src/train.py
```

### "Model seems to repeat"
```bash
# Need more training data
# Add files to data/

# Or train longer
python src/train.py --resume --epochs 50

# Or try higher temperature in chat
python src/cli.py --temp 0.9
```

## Using Make (If Available)

```bash
# Show all available commands
make help

# Setup
make setup

# Training
make train              # New training
make resume             # Continue training
make train-cpu          # Force CPU

# Chat
make cli                # Start chatting
make chat               # Same as cli

# Utilities
make status             # Check GPU and model
make clean              # Remove checkpoints
make data-size          # Show data size
```

## File Organization

After running everything:
```
Sirco-Gratify/
├── data/
│   ├── README.md           # Data instructions
│   ├── sample.md           # Example data (auto-created)
│   └── mydata.md           # Your data
├── checkpoints/
│   ├── checkpoint_v1.pt    # First training
│   ├── checkpoint_v2.pt    # Second training  
│   └── latest_model.pt     # Points to v2
├── user_data/
│   └── chat_history.json   # Your chats saved here
├── logs/                   # Training logs (if enabled)
└── src/
    ├── train.py
    ├── cli.py
    └── ...
```

## Common Workflows

### Workflow 1: Quick Start
```bash
# Setup
python setup.py

# Train on sample data
python src/train.py --epochs 5

# Chat
python src/cli.py
```

### Workflow 2: Production Training
```bash
# Add lots of data to data/

# Setup
python setup.py

# Train on GPU
python src/train.py --epochs 100 --batch-size 32

# Monitor
watch 'ls -lh checkpoints/checkpoint_v*.pt | tail -5'

# When done, chat
python src/cli.py
```

### Workflow 3: Continuous Improvement
```bash
# Day 1: Initial training
python src/train.py --epochs 50

# Day 2: Add more data
echo "More training text" >> data/newdata.md

# Resume training
python src/train.py --resume --epochs 50

# Day 3: Add even more
echo "More content" >> data/newdata.md
python src/train.py --resume --epochs 50

# Best model so far
python src/cli.py
```

### Workflow 4: Experimentation
```bash
# Backup current model
cp checkpoints/checkpoint_v5.pt backup_v5.pt

# Try different settings
python src/train.py --resume --lr 0.0001 --epochs 10

# Not good? Restore
rm checkpoints/checkpoint_v*.pt
cp backup_v5.pt checkpoints/checkpoint_v5.pt
```

## Performance Tips

### Speed Up Training
1. **Use GPU** - Already automatic, just ensure CUDA/ROCm installed
2. **Larger batches** - `--batch-size 64` (if VRAM allows)
3. **More data** - Add files to data/
4. **Multi-GPU** - Modify code (not automatic)

### Better Quality
1. **More data** - More diverse training data
2. **Longer training** - More epochs
3. **Larger model** - Bigger dimensions in config
4. **Better data** - High quality, coherent text

### Lower Memory Usage
1. **Smaller batches** - `--batch-size 4`
2. **Smaller model** - Reduce config values
3. **CPU training** - If VRAM limited
4. **Shorter sequences** - Modify max_seq_length

## Useful Commands

```bash
# Monitor GPU during training (in another terminal)
nvidia-smi watch -n 1         # NVIDIA GPUs
rocm-smi watch                # AMD GPUs
watch -n 1 'top -b -n1'       # CPU usage

# Check Python/PyTorch versions
python --version
python -c "import torch; print(torch.__version__)"

# Test GPU
python -c "from src.gpu_utils import detect_gpu; print(detect_gpu())"

# Run tests
python test_system.py

# Kill training gracefully
# Press Ctrl+C - will save checkpoint before exiting
```

## Getting Help

- `README.md` - Quick overview
- `TRAINING_GUIDE.md` - Detailed guide
- `ARCHITECTURE.md` - Technical architecture
- `data/README.md` - Training data help
- `checkpoints/README.md` - Checkpoint info
- `python src/train.py --help` - Training options
- `python src/cli.py --help` - Chat options

## Next Steps

1. **Setup**: Run `python setup.py`
2. **Verify**: Run `python test_system.py`
3. **Train**: Run `python src/train.py`
4. **Chat**: Run `python src/cli.py`
5. **Experiment**: Modify data, try different parameters
6. **Deploy**: Copy checkpoint to other machines

---

**Ready?** Start with: `python setup.py`

Questions? Check the docs above! 🚀
