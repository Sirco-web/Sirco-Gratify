#!/usr/bin/env python3
"""CLI for chatting with Gratify LLM."""

import sys
import torch
from pathlib import Path
from typing import List, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent))

from gpu_utils import setup_gpu_if_available, get_device_string, detect_gpu
from config import CHECKPOINTS_DIR, SYSTEM_BRAND, USER_DATA_DIR
from model import GratifyLLM


class GratifyChat:
    """Interactive chat interface for Gratify."""
    
    def __init__(self, checkpoint_path=None):
        """Initialize chat interface."""
        print(f"\n{'='*60}")
        print(f"🤖 {SYSTEM_BRAND['name']} - Interactive Chat")
        print(f"{'='*60}")
        
        # Setup GPU
        print("\n🔧 Checking GPU support...")
        gpu_info = detect_gpu()
        if gpu_info["available"]:
            print(f"✨ GPU: {gpu_info['type']} ({gpu_info['device_count']} device(s))")
        else:
            print("⚠️  Using CPU (consider installing GPU support for faster inference)")
        
        self.device = torch.device(get_device_string())
        
        # Load checkpoint
        print("\n📂 Loading model...")
        if checkpoint_path is None:
            checkpoint_path = self._get_latest_checkpoint()
        
        if checkpoint_path is None:
            print("❌ Error: No checkpoints found!")
            print(f"   Train the model first using: python train.py")
            sys.exit(1)
        
        self.checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        # Create model
        from config import GratifyConfig
        self.config = GratifyConfig.from_dict(self.checkpoint["config"])
        self.model = GratifyLLM(self.config).to(self.device)
        self.model.load_state_dict(self.checkpoint["model_state"])
        self.model.eval()
        
        # Tokenizer
        self._setup_tokenizer()
        
        # Conversation history
        self.history: List[Tuple[str, str]] = []
        self.user_data_file = USER_DATA_DIR / "chat_history.json"
        self._load_history()
        
        print(f"✅ Model loaded successfully!")
        print(f"   Architecture: {self.config.num_layers} layers, {self.config.num_heads} heads")
        print(f"   Context: {self.config.max_seq_length} tokens\n")
    
    def _get_latest_checkpoint(self):
        """Get the latest checkpoint."""
        checkpoints = list(CHECKPOINTS_DIR.glob("checkpoint_v*.pt"))
        if not checkpoints:
            return None
        versions = [(int(f.stem.split("_v")[-1]), f) for f in checkpoints]
        return max(versions, key=lambda x: x[0])[1]
    
    def _setup_tokenizer(self):
        """Setup character tokenizer."""
        # For simplicity, we'll recreate the tokenizer
        # In production, save vocabulary with checkpoint
        self.char_to_idx = {}
        self.idx_to_char = {}
        
        # We'll infer from model vocab size
        # For now, create a basic ASCII tokenizer
        chars = [chr(i) for i in range(32, 127)]  # Printable ASCII
        chars.extend(["\n", "\t", " "])
        
        for i, c in enumerate(sorted(set(chars))):
            self.char_to_idx[c] = i
            self.idx_to_char[i] = c
        
        # Ensure we have enough characters for vocab
        if self.config.vocab_size > len(self.char_to_idx):
            for i in range(len(self.char_to_idx), self.config.vocab_size):
                c = chr(i)
                self.char_to_idx[c] = i
                self.idx_to_char[i] = c
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        tokens = []
        for c in text:
            if c in self.char_to_idx:
                tokens.append(self.char_to_idx[c])
            else:
                # Use a special token for unknown characters
                tokens.append(0)
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs to text."""
        text = ""
        for idx in token_ids:
            if idx in self.idx_to_char:
                text += self.idx_to_char[idx]
            else:
                text += "?"
        return text
    
    def generate_response(self, prompt: str, max_tokens: int = 50, 
                         temperature: float = 0.7) -> str:
        """Generate a response from a prompt."""
        # Encode prompt
        prompt_ids = torch.tensor([self.encode(prompt)], dtype=torch.long)
        prompt_ids = prompt_ids.to(self.device)
        
        # Generate
        with torch.no_grad():
            generated = self.model.generate(
                prompt_ids,
                max_new_tokens=max_tokens,
                device=self.device,
                temperature=temperature
            )
        
        # Decode
        generated_text = self.decode(generated[0].cpu().tolist())
        response = generated_text[len(prompt):].strip()
        
        return response
    
    def _load_history(self):
        """Load chat history from file."""
        if self.user_data_file.exists():
            with open(self.user_data_file, "r") as f:
                try:
                    data = json.load(f)
                    self.history = [tuple(item) for item in data.get("history", [])]
                except json.JSONDecodeError:
                    self.history = []
    
    def _save_history(self):
        """Save chat history to file."""
        self.user_data_file.parent.mkdir(exist_ok=True)
        with open(self.user_data_file, "w") as f:
            json.dump({
                "history": self.history,
                "model": SYSTEM_BRAND["name"],
                "version": SYSTEM_BRAND["version"]
            }, f, indent=2)
    
    def print_welcome(self):
        """Print welcome message."""
        print("="*60)
        print(f"Welcome to {SYSTEM_BRAND['name']}!")
        print(f"I am {SYSTEM_BRAND['name']} by {SYSTEM_BRAND['author']}")
        print("="*60)
        print("Commands:")
        print("  'quit' or 'exit'  - Exit chat")
        print("  'clear'           - Clear history")
        print("  'history'         - Show chat history")
        print("  'about'           - Show model info")
        print("  'set temp X'      - Set temperature (0.0-1.0)")
        print("  'set tokens X'    - Set max response tokens")
        print("="*60 + "\n")
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns False if should exit."""
        command = user_input.lower().strip()
        
        if command in ["quit", "exit"]:
            print("👋 Goodbye!")
            return False
        
        elif command == "clear":
            self.history = []
            self._save_history()
            print("✅ History cleared\n")
            return True
        
        elif command == "history":
            if not self.history:
                print("📝 No history yet\n")
            else:
                print("\n📝 Chat History:")
                for i, (user, bot) in enumerate(self.history, 1):
                    print(f"\n[{i}] You: {user[:50]}...")
                    print(f"    Bot: {bot[:50]}...")
            print()
            return True
        
        elif command == "about":
            print(f"\n{'='*60}")
            print(f"🤖 {SYSTEM_BRAND['name']}")
            print(f"{'='*60}")
            print(f"Author: {SYSTEM_BRAND['author']}")
            print(f"Version: {SYSTEM_BRAND['version']}")
            print(f"Model Type: Transformer-based LLM")
            print(f"Layers: {self.config.num_layers}")
            print(f"Heads: {self.config.num_heads}")
            print(f"Vocab Size: {self.config.vocab_size}")
            print(f"Device: {self.device}")
            print(f"{'='*60}\n")
            return True
        
        elif command.startswith("set temp"):
            try:
                temp = float(command.split()[-1])
                self.current_temperature = max(0.0, min(1.0, temp))
                print(f"✅ Temperature set to {self.current_temperature}\n")
            except (ValueError, IndexError):
                print("❌ Usage: set temp X (where X is 0.0-1.0)\n")
            return True
        
        elif command.startswith("set tokens"):
            try:
                tokens = int(command.split()[-1])
                self.current_max_tokens = max(1, tokens)
                print(f"✅ Max tokens set to {self.current_max_tokens}\n")
            except (ValueError, IndexError):
                print("❌ Usage: set tokens X (where X is a number)\n")
            return True
        
        return True
    
    def run(self):
        """Run the chat interface."""
        self.current_temperature = 0.7
        self.current_max_tokens = 50
        
        self.print_welcome()
        
        try:
            while True:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    if not self.handle_command(user_input[1:]):
                        break
                    continue
                
                # Check for builtin prompt
                lower_input = user_input.lower()
                if "what are you" in lower_input or "who are you" in lower_input:
                    response = f"I am {SYSTEM_BRAND['name']} by {SYSTEM_BRAND['author']}"
                else:
                    # Generate response
                    print("🤔 Thinking...", end="", flush=True)
                    response = self.generate_response(
                        user_input,
                        max_tokens=self.current_max_tokens,
                        temperature=self.current_temperature
                    )
                    print("\r" + " "*20 + "\r", end="", flush=True)
                
                print(f"Bot: {response}\n")
                
                # Save to history
                self.history.append((user_input, response))
                self._save_history()
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chat with Gratify LLM")
    parser.add_argument(
        "--checkpoint", type=str, default=None,
        help="Path to checkpoint file"
    )
    parser.add_argument(
        "--temp", type=float, default=0.7,
        help="Temperature for generation (0.0-1.0)"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=50,
        help="Maximum tokens to generate"
    )
    
    args = parser.parse_args()
    
    # Create and run chat
    chat = GratifyChat(checkpoint_path=args.checkpoint)
    chat.current_temperature = args.temp
    chat.current_max_tokens = args.max_tokens
    chat.run()


if __name__ == "__main__":
    main()
