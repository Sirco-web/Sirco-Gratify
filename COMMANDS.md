# Gratify LLM - Quick Command Reference

## 📋 Setup Commands (Run Once)

```bash
# 1. Clone/navigate to project
cd Sirco-Gratify

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows (CMD):
venv\Scripts\activate.bat
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify setup works
python test_system.py
```

## 🧠 Training Commands

### Initial Training (Full Dataset)

```bash
# Train on all markdown files in data/md/
# 10 epochs, 16 batch size
python src/train.py --epochs 10 --batch-size 16

# Custom settings
python src/train.py --epochs 20 --batch-size 32 --lr 0.0005

# Resume from latest checkpoint
python src/train.py --resume --epochs 10

# List all training options
python src/train.py --help
```

### Fine-tuning (After Initial Training)

These commands are for training on NEW data after you already have a model:

```bash
# Add conversation data to data/finetune/ folder first
# Then fine-tune the model (uses lower learning rate)
python src/finetune.py --epochs 5

# Fine-tune with different settings
python src/finetune.py --epochs 3 --batch-size 8 --lr 1e-5

# Fine-tune from specific checkpoint
python src/finetune.py --checkpoint checkpoints/checkpoint_v2.pt --epochs 5

# List all fine-tuning options
python src/finetune.py --help
```

## 💬 Chat Commands

```bash
# Chat with the latest trained model
python src/cli.py

# Chat with specific checkpoint
python src/cli.py --checkpoint checkpoints/checkpoint_v1.pt

# Chat with custom settings
python src/cli.py --temp 0.9 --max-tokens 100
```

## 📚 Data Organization

```
data/
├── md/              ← Training data (markdown files)
│   ├── debugging_guide.md
│   ├── code_patterns.md
│   ├── common_bugs.md
│   ├── apis_web.md
│   ├── data_structures.md
│   └── sample.md
│
├── finetune/        ← Fine-tuning data (conversation data)
│   ├── conversation_1.md
│   ├── conversation_2.md
│   └── ... (add your conversation training data here)
│
└── README.md        ← Data folder documentation
```

## ✅ Typical Workflow

### First Time Setup
```bash
# Terminal 1: Setup
cd Sirco-Gratify
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python test_system.py
```

### Training the Model
```bash
# Terminal 1: Train on markdown files
python src/train.py --epochs 10

# This will:
# - Load all .md files from data/md/
# - Train for 10 epochs
# - Save checkpoint to checkpoints/checkpoint_v1.pt
```

### Using the Model
```bash
# Terminal 1: Chat with the trained model
python src/cli.py

# Example:
# You: what are you
# Bot: Gratify
#
# You: /about
# Bot: [Model information]
```

### Adding New Training Data & Fine-tuning
```bash
# 1. Add conversation data to data/finetune/ as .md files

# 2. Fine-tune (in terminal)
python src/finetune.py --epochs 5

# 3. Chat with improved model
python src/cli.py
```

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `python src/train.py` | Train from scratch on data/md/ |
| `python src/train.py --resume` | Continue training from checkpoint |
| `python src/finetune.py` | Fine-tune on data/finetune/ |
| `python src/cli.py` | Chat with the model |
| `python test_system.py` | Verify installation |

## 🔧 Virtual Environment Tricks

```bash
# Deactivate env when done
deactivate

# Delete env when not needed (frees space)
rm -rf venv

# Recreate env later
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📁 Project Structure

```
Sirco-Gratify/
├── data/
│   ├── md/              ← Your training markdown files
│   ├── finetune/        ← Your fine-tuning data
│   └── README.md
├── checkpoints/         ← Model checkpoints (auto-created)
├── user_data/           ← Chat history (auto-created)
├── src/
│   ├── train.py         ← Training script
│   ├── finetune.py      ← Fine-tuning script
│   ├── cli.py           ← Chat interface
│   ├── model.py         ← Model architecture
│   ├── config.py        ← Configuration
│   └── gpu_utils.py     ← GPU detection
├── venv/                ← Virtual environment (created with venv)
├── requirements.txt     ← Python packages to install
└── ... (other docs and configs)
```

## ❓ Troubleshooting

### "Module not found" error
```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### "No markdown files found"
```bash
# Add .md files to data/md/ folder
ls data/md/  # Check if files are there
```

### "No checkpoints found"
```bash
# Train first
python src/train.py --epochs 5
# Then chat
python src/cli.py
```

### GPU not detected but have GPU
```bash
# Run setup to install GPU drivers
python setup.py
```

## 📝 Notes

- Always activate venv before training: `source venv/bin/activate`
- Training on CPU: ~15-20 min for 10 epochs
- Training on GPU: ~1-2 min for 10 epochs
- Chat history saved in: `user_data/chat_history.json`
- Model checkpoints saved in: `checkpoints/checkpoint_v*.pt`

## 🚀 Done!

You're ready to:
1. ✅ Train your own LLM
2. ✅ Fine-tune it on custom data
3. ✅ Chat with your model
4. ✅ Keep upgrading it

Good luck! 🎉
