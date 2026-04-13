# 🚀 Quick Start Guide - Train on Your Laptop

Follow these exact steps to set up and train Gratify LLM on your laptop.

## ✅ Prerequisites

- Python 3.8+ installed
- ~5GB disk space
- ~4GB RAM minimum (8GB recommended)
- Text editor (VSCode, Sublime, etc.)

## 📋 Step-by-Step Setup

### Step 1: Navigate to Project

```bash
cd /path/to/Sirco-Gratify
```

### Step 2: Create Virtual Environment

This keeps your project isolated and clean.

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

After activation, you should see `(venv)` at the start of your terminal line.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs PyTorch and other requirements.

### Step 5: Verify Installation

```bash
python test_system.py
```

You should see all ✅ checkmarks.

## 🎯 Copy-Paste Command Sequences

### ⚡ FASTEST WAY (Copy & Paste)

Open a terminal in the project folder and run:

```bash
# Setup (one time only)
python -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python test_system.py

# Training (takes 10-15 minutes on CPU)
python src/train.py --epochs 5

# Chat with model
python src/cli.py
```

---

## 📚 File Organization

Your files are organized like this:

```
data/
├── md/                    ← TRAINING DATA (read-only)
│   ├── debugging_guide.md ✅ Already provided
│   ├── code_patterns.md   ✅ Already provided
│   ├── common_bugs.md     ✅ Already provided
│   ├── apis_web.md        ✅ Already provided
│   └── data_structures.md ✅ Already provided
│
└── finetune/              ← YOUR CONVERSATION DATA HERE
    ├── EXAMPLE.md         ← See example format
    └── (add your data here)
```

**The training script will:**
- Read .md files from `data/md/` folder
- Create model checkpoints in `checkpoints/` folder
- Save chat history in `user_data/` folder

---

## 🧠 Individual Commands Explained

### Training the Model

```bash
# Basic training (5 epochs on CPU = ~5-10 minutes)
python src/train.py --epochs 5

# More training = better model but takes longer
python src/train.py --epochs 10   # ~10-15 minutes

# With all options
python src/train.py --epochs 10 --batch-size 16 --lr 0.001

# Resume from where you left off
python src/train.py --resume --epochs 10
```

### Chatting with Model

```bash
# Start chatting
python src/cli.py

# Example chat:
# You: what are you
# Bot: Gratify
#
# You: how do i debug code
# Bot: [generates response about debugging]
#
# You: /quit
```

### Fine-tuning on Custom Data

First, add conversation data to `data/finetune/` folder. Then:

```bash
# Fine-tune (uses lower learning rate than training)
python src/finetune.py --epochs 3

# This improves the model with your custom data
```

---

## 🎓 Complete Beginner Steps

### First Time Users

1. **Open terminal in project folder**

2. **Copy & paste this entire block:**

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install everything
pip install -r requirements.txt

# Verify
python test_system.py
```

3. **When done, copy & paste this:**

```bash
# Make sure env is activated (you see "(venv)" in terminal)
# If not: source venv/bin/activate

# Train model (takes ~10 minutes first time)
python src/train.py --epochs 5

# When training finishes, run this to chat
python src/cli.py
```

4. **In the chat:**

```
Type: what are you
Model says: Gratify

Type: /about
Model says: [Model info]

Type: /quit
Exit chat
```

---

## ⏱️ Timing on Different Systems

| Hardware | 1 Epoch | 5 Epochs | 10 Epochs |
|----------|---------|----------|-----------|
| CPU (4 cores) | 3-5 min | 15-25 min | 30-50 min |
| CPU (8+ cores) | 2-3 min | 10-15 min | 20-30 min |
| GPU (NVIDIA) | 30 sec | 2-3 min | 5-7 min |
| GPU (AMD) | 45 sec | 3-4 min | 7-10 min |
| Laptop (CPU) | 4-6 min | 20-30 min | 40-60 min |

---

## 🎯 Recommended for Your Laptop

Start with fewer epochs to test:

```bash
# Test run (1-2 minutes)
python src/train.py --epochs 1

# Good quality (10-15 minutes)
python src/train.py --epochs 5

# Best quality (30-50 minutes, CPU)
python src/train.py --epochs 10
```

Then chat:

```bash
python src/cli.py
```

---

## 📊 Model Checkpoints

Each training creates a checkpoint:

```
checkpoints/
├── checkpoint_v1.pt    ← First training (5 epochs)
├── checkpoint_v2.pt    ← Second training 
├── checkpoint_v3.pt    ← Third training
└── latest_model.pt     ← Always the newest
```

The CLI automatically uses `latest_model.pt`.

---

## 🔧 Troubleshooting

### "command not found: python"
Use `python3` instead on some systems:
```bash
python3 -m venv venv
python3 test_system.py
```

### "No module named torch"
Make sure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### "No markdown files found"
The files should already be in `data/md/`
```bash
ls data/md/  # Check they exist
```

### Forgot to activate venv
You'll see errors. Activate it:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### "ModuleNotFoundError"
Reinstall requirements:
```bash
pip install -r requirements.txt
```

---

## 🚀 TL;DR (Too Long; Didn't Read)

```bash
# Setup (1 time)
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Train (10 min)
python src/train.py --epochs 5

# Chat (interactive)
python src/cli.py
```

Done! 🎉

---

## 📖 For More Details

- `README.md` - Project overview
- `COMMANDS.md` - All available commands
- `TRAINING_GUIDE.md` - Detailed training info
- `ARCHITECTURE.md` - Technical architecture

---

## ✨ Next Steps

1. ✅ Setup virtual environment
2. ✅ Install dependencies  
3. ✅ Train the model
4. ✅ Chat with it
5. ✅ (Optional) Add custom data to `data/finetune/` and fine-tune

**You've got this!** 🚀
