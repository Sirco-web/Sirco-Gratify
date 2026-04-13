.PHONY: help setup train cli chat test clean logs

# Gratify LLM Makefile

help:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║  Gratify LLM - Available Commands                      ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Setup & Installation:"
	@echo "   make setup       - Setup environment (auto-detects GPU)"
	@echo "   make install     - Install dependencies"
	@echo ""
	@echo "🧠 Training:"
	@echo "   make train       - Train model from scratch"
	@echo "   make resume      - Continue training from checkpoint"
	@echo "   make train-cpu   - Force CPU-only training"
	@echo ""
	@echo "💬 Interaction:"
	@echo "   make cli         - Start interactive chat"
	@echo "   make chat        - Alias for cli"
	@echo ""
	@echo "📊 Utilities:"
	@echo "   make clean       - Remove checkpoints and logs"
	@echo "   make logs        - Show training logs"
	@echo "   make status      - Check GPU and model status"
	@echo "   make data-size   - Show training data size"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "   make help        - Show this help message"
	@echo ""

setup:
	@echo "🚀 Setting up Gratify LLM..."
	python setup.py

install:
	@echo "📦 Installing dependencies..."
	python -m pip install -q -r requirements.txt

train:
	@echo "🧠 Starting training..."
	python src/train.py

resume:
	@echo "🧠 Resuming training from checkpoint..."
	python src/train.py --resume

train-cpu:
	@echo "🧠 Training on CPU..."
	CUDA_VISIBLE_DEVICES="" python src/train.py

cli:
	@echo "💬 Starting chat interface..."
	python src/cli.py

chat: cli

status:
	@echo "📊 Checking system status..."
	@python -c "from src.gpu_utils import detect_gpu; import json; gpu=detect_gpu(); print('GPU Status:', 'AVAILABLE' if gpu['available'] else 'NOT FOUND'); print(json.dumps(gpu, indent=2))" || echo "❌ Error checking GPU"
	@echo ""
	@echo "📂 Checkpoints:"
	@ls -lh checkpoints/ 2>/dev/null || echo "   (no checkpoints yet)"
	@echo ""
	@echo "💾 Data files:"
	@ls -lh data/ 2>/dev/null | grep ".md" || echo "   (no training data yet)"

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf checkpoints/checkpoint_v*.pt
	@rm -rf logs/
	@echo "✅ Cleaned"

logs:
	@echo "📋 Recent training logs:"
	@tail -f logs/*.log 2>/dev/null || echo "No logs found"

data-size:
	@echo "📊 Training data statistics:"
	@du -sh data/ 2>/dev/null || echo "0 B"
	@wc -l data/*.md 2>/dev/null | tail -1 || echo "0 lines"

.DEFAULT_GOAL := help
