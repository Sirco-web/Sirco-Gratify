# Gratify LLM - Technical Architecture

## Overview

Gratify is a complete, easy-to-use language model training framework with automatic GPU detection and a clean separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
├─────────────────────────────────────────────────────────┤
│  CLI (cli.py)      │  Training (train.py)                │
│  - Chat interface  │  - Epoch loop                       │
│  - Commands        │  - Checkpoint save/load             │
│  - History         │  - Progress tracking                │
└──────────┬──────────────────────┬───────────────────────┘
           │                      │
┌──────────▼──────────────────────▼───────────────────────┐
│                   Core Components                        │
├─────────────────────────────────────────────────────────┤
│  Model (model.py)  │  Config (config.py)                │
│  - Transformer     │  - Parameters                       │
│  - Token generation│  - Paths                            │
│  - Forward/eval    │  - Versioning                       │
└──────────┬──────────────┬───────────────────────────────┘
           │              │
┌──────────▼──────────────▼───────────────────────────────┐
│              Utilities & Infrastructure                  │
├─────────────────────────────────────────────────────────┤
│  GPU Utils (gpu_utils.py)      │  Data Loading          │
│  - CUDA detection              │  - Markdown parsing    │
│  - ROCm detection              │  - Tokenization        │
│  - Metal detection             │  - Batching            │
│  - Auto-installation           │                        │
└─────────────────────────────────────────────────────────┘
           │
┌──────────▼─────────────────────────────────────────────┐
│              Hardware (Auto-managed)                     │
├─────────────────────────────────────────────────────────┤
│  GPU (CUDA/ROCm/Metal)  │  CPU (Fallback)              │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/
├── __init__.py           # Package initialization
├── gpu_utils.py          # GPU detection & management
├── config.py             # Configuration & paths
├── model.py              # Model architecture
├── train.py              # Training loop
└── cli.py                # Chat interface

data/
├── README.md             # Instructions
├── sample.md             # Example training data
└── *.md                  # User's training data

checkpoints/
├── README.md             # Checkpoint guide
├── checkpoint_v1.pt      # Version 1
├── checkpoint_v2.pt      # Version 2
└── latest_model.pt       # Latest version

user_data/
├── README.md             # User data info
└── chat_history.json     # Chat history

Root files:
├── setup.py              # Initial setup
├── requirements.txt      # Dependencies
├── test_system.py        # System verification
├── quickstart.sh         # Quick start script
├── Makefile              # Convenience commands
├── README.md             # Main readme
└── TRAINING_GUIDE.md     # Detailed guide
```

## GPU Detection & Initialization

### Detection Process

```python
1. Check NVIDIA CUDA via torch.cuda
   └─> Success: CUDA mode
   
2. Check AMD ROCm via rocm-smi command
   └─> Success: ROCm mode
   
3. Check Apple Metal on macOS
   └─> Success: Metal mode
   
4. Fallback to CPU
```

### Installation Flow

When GPU is detected:
```
1. Identify GPU type (CUDA/ROCm/Metal)
2. Install GPU-specific PyTorch version
3. Set device string (cuda:0, cuda:1, etc.)
4. Configure training for GPU acceleration
```

### Device Selection

```python
get_device_string()
├─> CUDA available? → "cuda:0"
├─> Metal available? → "mps"
└─> Fallback → "cpu"
```

## Model Architecture

### Transformer-based LLM

```
Input Tokens
    │
    ▼
Embedding Layer (Vocab → 256-dim)
    │
    ▼
Positional Encoding (Add sequence position info)
    │
    ▼
┌──────────────────────────┐
│ Transformer Blocks x 4   │  ◄─ Configurable
├──────────────────────────┤
│ 1. Multi-Head Attention  │
│    (8 heads)             │
│    │
│    ▼
│ 2. Layer Norm            │
│    │
│    ▼
│ 3. Feed-Forward Network  │
│    (256 → 512 → 256)     │
│    │
│    ▼
│ 4. Layer Norm            │
│    │
│    ▼
│ 5. Residual Connections  │
└──────────────────────────┘
    │
    ▼
Final Layer Norm
    │
    ▼
Output Linear Layer → Logits
    │
    ▼
Softmax → Probability Distribution
    │
    ▼
Output Tokens
```

### Configuration

```python
GratifyConfig:
  vocab_size = 10000         # Character vocabulary
  embedding_dim = 256        # Token embedding dimension
  num_layers = 4             # Transformer layers
  num_heads = 8              # Attention heads
  hidden_dim = 512           # FFN hidden dimension
  max_seq_length = 512       # Context window
  dropout = 0.1              # Regularization
```

## Training Pipeline

### Training Loop

```
1. Load data from data/*.md files
2. Create character-level tokenizer
3. Initialize model & optimizer
4. For each epoch:
   a. For each batch:
      i.   Forward pass: get logits
      ii.  Calculate loss (CrossEntropy)
      iii. Backward pass
      iv.  Gradient clipping
      v.   Optimizer step
      vi.  Save checkpoint (every N steps)
   b. Log progress
5. Save final checkpoint
```

### Checkpoint System

```
Checkpoint Structure:
{
  "version": 5,                    # Checkpoint number
  "model_state": {...},            # Model weights
  "optimizer_state": {...},        # Adam state
  "global_step": 50000,            # Training steps
  "config": {...},                 # Model config
  "brand": {                       # Metadata
    "name": "Gratify",
    "author": "sirco",
    "version": "0.1.0"
  }
}

Naming Convention:
checkpoint_v1.pt  → First training
checkpoint_v2.pt  → Resume/continue
checkpoint_vN.pt  → Nth training session
latest_model.pt   → Always points to latest
```

## CLI (Chat Interface)

### Command Processing

```
User Input
    │
    ├─ Starts with '/'?
    │  └─> Command type
    │      ├─ /quit, /exit → Exit program
    │      ├─ /clear → Clear history
    │      ├─ /history → Show past chats
    │      ├─ /about → Show model info
    │      ├─ /set temp X → Set temperature
    │      └─ /set tokens X → Set max tokens
    │
    ├─ "what are you" or "who are you"?
    │  └─> Return built-in response:
    │      "I am Gratify by sirco"
    │
    └─> Generate response via model
        ├─ Tokenize input
        ├─ Forward pass through model
        ├─ Sample from output distribution
        ├─ Decode to text
        └─ Return response

Save to chat_history.json
Display to user
```

### Temperature Control

```
Temperature Purpose: Control randomness in generation

Low temp (0.1):   Very deterministic, repetitive
Medium temp (0.7): Balanced, natural
High temp (1.0+): Very random, creative

Implementation:
1. Get logits from model
2. Divide by temperature: logits / temp
3. Apply softmax
4. Sample from distribution
```

## Data Flow

### Training Data Processing

```
data/*.md files
    │
    ▼
Read all files (concatenate)
    │
    ▼
Character-level tokenization
char_to_idx: {'a': 0, 'b': 1, ...}
idx_to_char: {0: 'a', 1: 'b', ...}
    │
    ▼
Create sequences of length N
[token_0, token_1, ..., token_N]
    │
    ▼
Create (input, target) pairs
[token_0...N-1] → [token_1...N]
    │
    ▼
Batch into groups of B
    │
    ▼
GPU Transfer (if GPU available)
    │
    ▼
Model Training
```

### Inference (Chat) Data Flow

```
User prompt
    │
    ▼
Tokenize: prompt → token_ids
    │
    ▼
Generate loop (max_new_tokens times):
  1. Forward pass: logits = model(token_ids)
  2. Get last token logits
  3. Apply temperature
  4. Sample next token
  5. Append to sequence
  6. Keep last 512 tokens (context window)
    │
    ▼
Detokenize: token_ids → text
    │
    ▼
Display to user
```

## GPU Acceleration

### Memory Layout

```
GPU VRAM:
┌──────────────────────────────────┐
│ Model Parameters: ~100 MB        │
├──────────────────────────────────┤
│ Batch Data: ~256 MB per batch    │
├──────────────────────────────────┤
│ Gradients: ~100 MB               │
├──────────────────────────────────┤
│ Optimizer State: ~200 MB (Adam)  │
├──────────────────────────────────┤
│ Activation Cache: ~256 MB        │
├──────────────────────────────────┤
│ Free Memory: Remaining           │
└──────────────────────────────────┘
Total: 4-8 GB typical
```

### Performance Characteristics

```
CPU (Intel i7, 8 cores):
- Throughput: 5-20 samples/sec
- Latency: 50-200ms per sample
- Memory: 4-16 GB RAM

NVIDIA CUDA (RTX 3080):
- Throughput: 100-200 samples/sec
- Latency: 5-10ms per sample
- Memory: 2-4 GB VRAM
- Speedup: 10-50x

Apple Metal (M1 Pro):
- Throughput: 30-100 samples/sec
- Latency: 10-33ms per sample
- Memory: 1-2 GB shared
- Speedup: 5-20x
```

## Key Design Decisions

### 1. Character-Level Tokenization
- **Pro**: Works with any text, no OOV issues
- **Con**: Longer sequences, larger vocab
- **Use**: Simple, flexible for learning

### 2. PyTorch Framework
- **Pro**: Production-ready, good GPU support
- **Con**: Heavier than TensorFlow
- **Use**: Industry standard, easy to deploy

### 3. Simple Architecture
- **Pro**: Easy to understand, train, modify
- **Con**: Not state-of-the-art
- **Use**: Learning tool, prototype, proof-of-concept

### 4. Auto GPU Detection
- **Pro**: Works out of box, no manual setup
- **Con**: Doesn't handle all edge cases
- **Use**: Beginner-friendly, good UX

### 5. Checkpoint Versioning
- **Pro**: Never lose trained models
- **Con**: Uses disk space
- **Use**: Resume, experiment, compare

## Extensibility

### Adding Features

1. **Better Tokenizer** → Modify config.py, train.py
2. **Larger Model** → GratifyConfig in config.py
3. **Multi-GPU Training** → train.py with DataParallel
4. **Fine-tuning** → Load checkpoint, train on new data
5. **Web API** → Wrap cli.py in Flask/FastAPI
6. **Quantization** → torch.quantization in cli.py

### Common Modifications

```python
# Bigger model
config.embedding_dim = 512
config.num_layers = 8
config.hidden_dim = 1024

# Better learning
config.learning_rate = 5e-4
config.warmup_steps = 1000

# Larger batches (if VRAM allows)
config.batch_size = 64

# Longer training
python src/train.py --epochs 100
```

## Error Handling & Recovery

### Training Failures
- Checkpoint saved every N steps → Resume from last checkpoint
- Gradient clipping prevents NaN
- Device fallback: GPU issue? → Use CPU

### Chat Failures
- No checkpoint? → Setup wizard prevents
- Out of memory? → Reduce batch size
- Slow inference? → Can't fix at runtime, adjust model size

### Data Issues
- No .md files? → sample.md created, instructions shown
- Corrupt data? → Graceful skip, continue
- Empty data? → Clear warning shown

## Deployment

### Single Machine
```bash
python src/cli.py
```

### Server
```python
# Convert to API
from flask import Flask
from src.cli import GratifyChat

app = Flask(__name__)
chat = GratifyChat()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    prompt = request.json['prompt']
    response = chat.generate_response(prompt)
    return {"response": response}

app.run()
```

### Mobile/Edge
```python
# Export checkpoint, run on device with PyTorch
import torch
checkpoint = torch.load("checkpoint_v5.pt")
# Load on device...
```

## Security Considerations

- No network access (local only by default)
- No untrusted code execution
- File access limited to project directory
- No credential handling

## Future Roadmap

- [ ] BPE/WordPiece tokenizer
- [ ] Distributed training
- [ ] Model quantization & compression
- [ ] Web UI
- [ ] Fine-tuning mode
- [ ] Export to ONNX
- [ ] Mobile inference
- [ ] Real-time streaming

---

**Gratify LLM Architecture** - Designed for simplicity and effectiveness
