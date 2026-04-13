# Example Fine-tuning Data

This is an example of how to format conversation data for fine-tuning.

## Example Conversation Format

When fine-tuning on conversations, create markdown files in this format:

### Q&A Format

```
# Question: How do I debug a Python error?

Answer: To debug a Python error, you should follow these steps:

1. Read the error message carefully - it tells you what's wrong
2. Identify the line causing the issue using the traceback
3. Check variable values at that point
4. Use print statements or a debugger to inspect state
5. Test your fix before moving on

# Question: What's the fastest data structure for lookups?

Answer: Use a dictionary (hash map). It has O(1) lookup time, much faster than lists which are O(n).
```

### Chat Format

```
You: what's the best way to optimize this code?
Bot: First, identify the bottleneck using a profiler. Then optimize the slowest part. Common optimizations: use better algorithms, cache values, use faster data structures, or move to compiled code.

You: explain REST APIs
Bot: REST APIs use HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources identified by URLs. They return JSON responses and use standard HTTP status codes.
```

## How to Add Fine-tuning Data

1. Create a `.md` file in this folder (e.g., `my_conversations.md`)
2. Add Q&A or chat data in the format above
3. Run: `python src/finetune.py --epochs 5`
4. Chat with improved model: `python src/cli.py`

## Benefits of Fine-tuning

- Adapt model to your specific domain
- Teach it custom responses
- Improve quality on specific topics
- Use less training time (lower learning rate)
- Keep existing knowledge while adding new

## Example Files to Create

`coding_qa.md` - Q&A about coding problems
`debugging_tips.md` - Debugging techniques
`api_design.md` - API design patterns
`custom_responses.md` - Custom responses for your use case
