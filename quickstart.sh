#!/bin/bash
# Quick start script for Gratify LLM

set -e

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           🚀 Gratify LLM - Quick Start                ║"
echo "║           Language Model Training System              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python $python_version"

# Run setup
echo ""
echo "📦 Running setup..."
python setup.py

# Verify structure
echo ""
echo "✅ Files created:"
echo "   data/              - Add .md training files here"
echo "   user_data/         - Chat history will be saved here"
echo "   checkpoints/       - Model versions stored here"
echo "   src/               - Training and CLI code"

echo ""
echo "═════════════════════════════════════════════════════════"
echo "🎉 Setup Complete! Next steps:"
echo "═════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  (OPTIONAL) Add more training data to data/ directory"
echo "2️⃣  Start training:"
echo "   python src/train.py"
echo ""
echo "3️⃣  Chat with your model:"  
echo "   python src/cli.py"
echo ""
echo "📚 For detailed info, see TRAINING_GUIDE.md"
echo ""
echo "═════════════════════════════════════════════════════════"
