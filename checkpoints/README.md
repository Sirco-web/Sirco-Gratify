# Model Checkpoints Directory

This directory stores versioned model checkpoints during and after training.

## Checkpoint System

Each training run creates numbered checkpoints:

```
checkpoints/
├── checkpoint_v1.pt   # Initial training session
├── checkpoint_v2.pt   # Continued training / 2nd session  
├── checkpoint_v3.pt   # 3rd session
├── checkpoint_vN.pt   # And so on...
└── latest_model.pt    # Symlink to most recent
```

## What's in a Checkpoint?

Each `.pt` file contains:
- **Model weights** - The trained neural network parameters
- **Optimizer state** - For resuming training
- **Step count** - How many training steps completed
- **Config** - Model configuration used
- **Version info** - Metadata about the model

## Using Checkpoints

### Resume Training
```bash
# Automatically uses latest
python src/train.py --resume

# Continue for more epochs
python src/train.py --resume --epochs 10
```

### Load for Inference
```bash
# CLI automatically uses latest checkpoint
python src/cli.py

# Specify specific checkpoint
python src/cli.py --checkpoint checkpoints/checkpoint_v5.pt
```

### Sharing Models
```bash
# Copy any checkpoint to share
cp checkpoints/checkpoint_v5.pt my_model.pt

# Others can use it
python src/cli.py --checkpoint my_model.pt
```

## Checkpoint Naming

- **checkpoint_v1.pt** - Training run #1
- **checkpoint_v2.pt** - Training run #2
- **checkpoint_v_X.pt** - Training run #X

Versions auto-increment so you never overwrite trained models!

## Version History

Keep multiple versions to:
- Experiment with different configurations
- Rollback if things go wrong
- Compare model performance over time
- Save best performing versions

## Storage Considerations

- Each checkpoint: ~50-200 MB depending on model size
- Keep important versions, delete failed experiments
- Archive to external storage for long-term storage

## Best Practices

1. **After successful training** - Keep the checkpoint
2. **Before major changes** - Back up current checkpoint
3. **Testing new ideas** - Can always resume from known good checkpoint
4. **Production use** - Use specific tested checkpoint version

## Version Tracking

Track which version was trained on what data:

```
v1: Initial training on sample.md (100 epochs)
v2: Added book.md, fine-tuned (50 epochs) 
v3: Added documentation.md (100 epochs)
v4: Parameter tuning experiments (20 epochs) - deleted
v5: Best version before major changes
```

---

Checkpoints are created automatically during training.
Keep them! They represent your trained models.
