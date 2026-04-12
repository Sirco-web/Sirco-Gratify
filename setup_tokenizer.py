"""
Tokenizer setup and training
Uses SentencePiece for subword tokenization (like LLaMA)
"""

import sentencepiece as spm
from pathlib import Path
import os


class TokenizerManager:
    """Manage tokenizer training and loading"""
    
    def __init__(self, model_dir="tokenizers"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
    
    def train_tokenizer(self, input_file, model_prefix="tokenizer", vocab_size=32000, 
                       model_type="bpe", character_coverage=0.9995):
        """
        Train a SentencePiece tokenizer
        
        Args:
            input_file: Path to text file for training
            model_prefix: Prefix for output model files
            vocab_size: Size of vocabulary
            model_type: 'bpe', 'unigram', 'char', or 'word'
            character_coverage: % of characters to cover
        
        Returns:
            Path to trained model file
        """
        
        model_path = self.model_dir / model_prefix
        model_file = model_path.with_suffix('.model')
        
        if model_file.exists():
            print(f"Tokenizer already exists: {model_file}")
            return str(model_file)
        
        print(f"Training {vocab_size}-size {model_type} tokenizer...")
        print(f"Input: {input_file}")
        print(f"Output: {model_file}")
        
        spm.SentencePieceTrainer.train(
            input=str(input_file),
            model_prefix=str(model_path),
            vocab_size=vocab_size,
            model_type=model_type,
            character_coverage=character_coverage,
            num_threads=os.cpu_count(),
            normalization_rule_name="identity",  # No lowercasing
            split_digits=True,
            unk_surface="<unk>",
            unk_id=0,
            bos_id=1,
            eos_id=2,
            pad_id=-1,  # Disabled
        )
        
        print(f"✓ Tokenizer trained")
        
        return str(model_file)
    
    def load_tokenizer(self, model_file):
        """Load a trained tokenizer"""
        model_file = Path(model_file)
        
        if not model_file.exists():
            raise FileNotFoundError(f"Tokenizer model not found: {model_file}")
        
        sp = spm.SentencePieceProcessor(model_file=str(model_file))
        
        print(f"Loaded tokenizer: {model_file}")
        print(f"  Vocab size: {sp.get_piece_size()}")
        print(f"  BOS ID: {sp.bos_id()}")
        print(f"  EOS ID: {sp.eos_id()}")
        print(f"  UNK ID: {sp.unk_id()}")
        
        return sp
    
    def test_tokenizer(self, tokenizer, test_text):
        """Test tokenizer on sample text"""
        print(f"\nTesting tokenizer:")
        print(f"  Input: {test_text}")
        
        tokens = tokenizer.encode(test_text)
        print(f"  Tokens ({len(tokens)}): {tokens}")
        
        pieces = tokenizer.encode_as_pieces(test_text)
        print(f"  Pieces: {pieces}")
        
        decoded = tokenizer.decode(tokens)
        print(f"  Decoded: {decoded}")
    
    def get_tokenizer_info(self, tokenizer):
        """Print detailed tokenizer info"""
        print("\nTokenizer Information:")
        print(f"  Vocab size: {tokenizer.get_piece_size()}")
        print(f"  BOS ID: {tokenizer.bos_id()}")
        print(f"  EOS ID: {tokenizer.eos_id()}")
        print(f"  UNK ID: {tokenizer.unk_id()}")
        print(f"  PAD ID: {tokenizer.pad_id()}")
        
        # Sample tokens
        print(f"\n  First 10 tokens:")
        for i in range(min(10, tokenizer.get_piece_size())):
            piece = tokenizer.id_to_piece(i)
            print(f"    {i:5d}: {piece}")
        
        print(f"\n  Last 10 tokens:")
        for i in range(max(0, tokenizer.get_piece_size()-10), tokenizer.get_piece_size()):
            piece = tokenizer.id_to_piece(i)
            print(f"    {i:5d}: {piece}")


def setup_tokenizer(data_file="data/processed/combined.txt", 
                   vocab_size=32000,
                   tokenizer_dir="tokenizers"):
    """
    Complete tokenizer setup pipeline
    """
    
    print("=" * 60)
    print("Tokenizer Setup")
    print("=" * 60)
    
    # Check if data file exists
    data_file = Path(data_file)
    if not data_file.exists():
        print(f"\n⚠ Data file not found: {data_file}")
        print("Run: python data_prep.py")
        return None
    
    manager = TokenizerManager(model_dir=tokenizer_dir)
    
    # Train tokenizer
    print("\n[1] Training tokenizer...")
    print("-" * 60)
    model_file = manager.train_tokenizer(
        input_file=data_file,
        model_prefix="tokenizer",
        vocab_size=vocab_size,
        model_type="bpe"
    )
    
    # Load tokenizer
    print("\n[2] Loading tokenizer...")
    print("-" * 60)
    tokenizer = manager.load_tokenizer(model_file)
    
    # Test tokenizer
    print("\n[3] Testing tokenizer...")
    print("-" * 60)
    test_texts = [
        "Hello, world!",
        "Machine learning is fascinating.",
        "The quick brown fox jumps over the lazy dog.",
    ]
    
    for text in test_texts:
        manager.test_tokenizer(tokenizer, text)
        print()
    
    # Get info
    print("\n[4] Tokenizer information...")
    print("-" * 60)
    manager.get_tokenizer_info(tokenizer)
    
    print("\n[✓] Tokenizer setup complete!")
    print(f"Model: {model_file}")
    
    return tokenizer, model_file


if __name__ == "__main__":
    """Setup tokenizer with default settings"""
    # Check if combined.txt exists first
    data_file = "data/processed/combined.txt"
    
    if not Path(data_file).exists():
        print(f"Data file not found: {data_file}")
        print("\nPlease run: python data_prep.py")
        print("This will prepare the training data.")
    else:
        setup_tokenizer(data_file=data_file)
