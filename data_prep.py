"""
Data preparation for LLM training
Downloads and preprocesses text data for training
"""

import os
import json
import requests
import gzip
import shutil
from pathlib import Path
import random
import re
from tqdm import tqdm


class DataPreparer:
    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.raw_dir = self.output_dir / "raw"
        self.processed_dir = self.output_dir / "processed"
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

    def download_file(self, url, filename):
        """Download a file from URL"""
        filepath = self.raw_dir / filename
        
        if filepath.exists():
            print(f"File already exists: {filepath}")
            return filepath
        
        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            if total_size > 0:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            else:
                f.write(response.content)
        
        print(f"Downloaded to {filepath}")
        return filepath

    def extract_gz(self, filepath):
        """Extract gzip file"""
        output_path = filepath.with_suffix('')
        
        if output_path.exists():
            print(f"File already extracted: {output_path}")
            return output_path
        
        print(f"Extracting {filepath}...")
        with gzip.open(filepath, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"Extracted to {output_path}")
        return output_path

    def clean_text(self, text):
        """Preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        return text.strip()

    def create_dataset_from_text(self, text_files, output_name="dataset.txt", chunk_size=1000000):
        """Create training dataset from text files"""
        output_path = self.processed_dir / output_name
        
        if output_path.exists():
            print(f"Dataset already exists: {output_path}")
            file_size = output_path.stat().st_size / (1024**2)
            print(f"  Size: {file_size:.1f} MB")
            return output_path
        
        print(f"Creating dataset from {len(text_files)} files...")
        
        with open(output_path, 'w', encoding='utf-8') as out_f:
            total_size = 0
            
            for text_file in text_files:
                if not Path(text_file).exists():
                    print(f"  Warning: File not found: {text_file}")
                    continue
                
                print(f"  Processing: {text_file}")
                
                try:
                    with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in tqdm(f, desc=f"  {Path(text_file).name}"):
                            cleaned = self.clean_text(line)
                            if cleaned:
                                out_f.write(cleaned + '\n')
                                total_size += len(cleaned) + 1
                except Exception as e:
                    print(f"  Error processing {text_file}: {e}")
        
        file_size = output_path.stat().st_size / (1024**2)
        print(f"Dataset created: {output_path}")
        print(f"  Size: {file_size:.1f} MB")
        return output_path

    def download_wikitext(self):
        """Download WikiText dataset"""
        # WikiText-103 gzip file
        url = "https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip"
        # Note: Using a simpler alternative since the original requires 2GB+
        
        # For demo, download a smaller dataset
        wiki_files = []
        try:
            print("Downloading WikiText sample...")
            # Download from a mirror or use a smaller subset
            filepath = self.raw_dir / "wikitext_sample.txt"
            if not filepath.exists():
                # Create sample data for demo
                print("Creating sample WikiText data...")
                sample_text = """
The United Nations is an intergovernmental organization that aims to maintain international peace and security.
Wikipedia is a free online encyclopedia created collaboratively by volunteers around the world.
Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience.
Deep learning is a more specialized form of machine learning that mimics the way neurons work in human brains.
Natural language processing is a field of artificial intelligence concerned with the interactions between computers and human language.
Transformer models have become a dominant architecture in modern machine learning and natural language processing.
The attention mechanism is a key component that allows models to focus on relevant parts of the input.
Large language models are neural networks trained on vast amounts of text data from the internet.
Training a model requires careful selection of hyperparameters and optimization techniques.
Gradient descent is the fundamental optimization algorithm used in training neural networks.
Backpropagation is the method of computing gradients through a neural network.
Regularization techniques help prevent overfitting in machine learning models.
Batch normalization improves training stability and allows higher learning rates.
Dropout randomly deactivates neurons to prevent co-adaptation during training.
Cross-entropy loss is a common loss function for classification tasks.
Perplexity is a measure of how well a probability model predicts a sample.
Tokenization is the process of breaking text into individual tokens for processing.
Embeddings are dense vector representations of tokens or words in high-dimensional space.
Positional encoding helps models understand the order of tokens in a sequence.
Vocabulary size determines the number of unique tokens a model can process.
                """
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(sample_text)
            wiki_files.append(str(filepath))
        except Exception as e:
            print(f"Error downloading WikiText: {e}")
        
        return wiki_files

    def download_common_crawl(self):
        """Download Common Crawl sample (very large, returns empty for demo)"""
        # Common Crawl is massive, we'll skip the actual download for demo
        # In production, you'd download from https://commoncrawl.org/
        print("Common Crawl is very large (hundreds of GB). Skipping for demo.")
        return []

    def download_books(self):
        """Download Project Gutenberg books"""
        book_files = []
        
        # Sample of famous public domain books
        book_urls = [
            # These are example URLs - they may need updating
            # For demo, we'll create synthetic data
        ]
        
        try:
            print("Creating sample book data...")
            filepath = self.raw_dir / "books_sample.txt"
            if not filepath.exists():
                sample_text = """
It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness.
In the beginning God created the heavens and the earth.
Call me Ishmael. Some years ago, never mind how long precisely, having little or no money in my purse.
It is a truth universally acknowledged that a single man in possession of a good fortune must be in want of a wife.
The great gray beast had been steadily working its way across the meadow and had finally detected their scent.
It was a pleasure to burn. It was a special pleasure to see things eaten, to see things blackened and changed.
The past is a foreign country; they do things differently there.
Happy families are all alike; every unhappy family is unhappy in its own way.
You better not never tell nobody but God. I had to go north.
It was love at first sight. The first time Yossarian saw the chaplain, he fell madly in love with him.
                """
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(sample_text * 100)  # Repeat to make it larger
            book_files.append(str(filepath))
        except Exception as e:
            print(f"Error with books: {e}")
        
        return book_files

    def split_train_val_test(self, dataset_file, train_ratio=0.8, val_ratio=0.1):
        """Split dataset into train/val/test"""
        dataset_file = Path(dataset_file)
        
        train_file = self.processed_dir / "train.txt"
        val_file = self.processed_dir / "val.txt"
        test_file = self.processed_dir / "test.txt"
        
        if all([f.exists() for f in [train_file, val_file, test_file]]):
            print(f"Train/val/test already exist, skipping split")
            return train_file, val_file, test_file
        
        print(f"Splitting {dataset_file}...")
        
        # Count lines
        with open(dataset_file, 'r', encoding='utf-8') as f:
            num_lines = sum(1 for _ in f)
        
        print(f"Total lines: {num_lines}")
        
        # Create splits
        with open(dataset_file, 'r', encoding='utf-8') as f_in:
            with open(train_file, 'w', encoding='utf-8') as f_train, \
                 open(val_file, 'w', encoding='utf-8') as f_val, \
                 open(test_file, 'w', encoding='utf-8') as f_test:
                
                for i, line in enumerate(tqdm(f_in, total=num_lines, desc="Splitting")):
                    rand = random.random()
                    if rand < train_ratio:
                        f_train.write(line)
                    elif rand < train_ratio + val_ratio:
                        f_val.write(line)
                    else:
                        f_test.write(line)
        
        print(f"Train: {train_file}")
        print(f"Val: {val_file}")
        print(f"Test: {test_file}")
        
        return train_file, val_file, test_file

    def get_dataset_stats(self, filepath):
        """Print dataset statistics"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return
        
        print(f"\nDataset Statistics: {filepath}")
        print("-" * 50)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = 0
            chars = 0
            words = 0
            
            for line in f:
                lines += 1
                chars += len(line)
                words += len(line.split())
        
        file_size = filepath.stat().st_size / (1024**2)
        
        print(f"  File size: {file_size:.2f} MB")
        print(f"  Lines: {lines:,}")
        print(f"  Characters: {chars:,}")
        print(f"  Words: {words:,}")
        print(f"  Avg chars per line: {chars/max(1,lines):.1f}")
        print(f"  Avg words per line: {words/max(1,lines):.1f}")


def main():
    """Main data preparation pipeline"""
    print("=" * 60)
    print("LLM Training Data Preparation")
    print("=" * 60)
    
    preparer = DataPreparer()
    
    # Step 1: Download data sources
    print("\n[1] Downloading data sources...")
    print("-" * 60)
    
    text_files = []
    
    # WikiText
    wiki_files = preparer.download_wikitext()
    text_files.extend(wiki_files)
    
    # Books
    book_files = preparer.download_books()
    text_files.extend(book_files)
    
    # Common Crawl (optional - very large)
    # cc_files = preparer.download_common_crawl()
    # text_files.extend(cc_files)
    
    if not text_files:
        print("No data files found. Creating sample dataset...")
        sample_file = preparer.raw_dir / "sample.txt"
        with open(sample_file, 'w') as f:
            f.write("Sample training data.\n" * 1000)
        text_files = [str(sample_file)]
    
    # Step 2: Create combined dataset
    print("\n[2] Creating combined dataset...")
    print("-" * 60)
    dataset_file = preparer.create_dataset_from_text(text_files, "combined.txt")
    
    # Step 3: Get stats
    print("\n[3] Dataset statistics...")
    print("-" * 60)
    preparer.get_dataset_stats(dataset_file)
    
    # Step 4: Split into train/val/test
    print("\n[4] Splitting dataset...")
    print("-" * 60)
    train_file, val_file, test_file = preparer.split_train_val_test(dataset_file)
    
    # Step 5: Print final stats
    print("\n[5] Final dataset statistics...")
    print("-" * 60)
    for name, filepath in [("Train", train_file), ("Val", val_file), ("Test", test_file)]:
        preparer.get_dataset_stats(filepath)
    
    print("\n[✓] Data preparation complete!")
    print(f"Data directory: {preparer.output_dir}")


if __name__ == "__main__":
    main()
