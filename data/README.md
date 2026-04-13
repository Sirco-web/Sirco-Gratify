# Training Data Directory

Add your `.md` (markdown) files here to train the model.

## About Training Data

The model learns from all text in these markdown files:
- **More data = Better model** (generally)
- **Quality matters** - Coherent text works better than random text
- **Diversity helps** - Mix different topics and writing styles

## Suggested Data Sources

1. **Books and Literature**
   - Project Gutenberg (public domain books)
   - Classic literature

2. **Documentation**
   - API documentation
   - Technical guides
   - How-to articles

3. **Web Content**
   - Blog posts
   - Educational articles
   - README files

4. **Your Own Content**
   - Domain-specific knowledge
   - Custom written text
   - Domain data for specialized models

## File Format

Use `.md` (markdown) format. Each file should contain:
```markdown
# Title

Content here...

## Section

More content...
```

## How to Use

1. Place `.md` files in this directory
2. Run: `python src/train.py`
3. Model learns from all files

## Notes

- Files are read in any order
- All text combined into training dataset
- Character-level tokenization used by default
- Can train on multiple files (training data size = sum of all files)

## Example Workflow

```bash
# Download training data
wget https://example.com/book.md -O data/book.md

# Add your own data
echo "# My Data" > data/custom.md
echo "Your training content here" >> data/custom.md

# Train model
python src/train.py

# Train more
python src/train.py --resume --epochs 10
```

Good luck! 🚀
