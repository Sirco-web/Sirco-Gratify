import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import sentencepiece as spm
import os
from pathlib import Path
import json

# =========================
# CONFIG
# =========================
class Config:
    dim = 256
    heads = 8
    layers = 6
    seq_len = 256
    vocab_size = 32000

    tp_size = torch.cuda.device_count() if torch.cuda.is_available() else 1

    lr = 3e-4
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Training
    batch_size = 32
    num_epochs = 10
    warmup_steps = 1000
    max_steps = 100000
    
    # Checkpointing
    checkpoint_dir = "checkpoints"
    save_interval = 1000


# =========================
# TOKENIZER (SentencePiece = real LLaMA style)
# =========================
class Tokenizer:
    def __init__(self, model_file="tokenizer.model"):
        self.sp = spm.SentencePieceProcessor(model_file=model_file)

    def encode(self, text):
        return self.sp.encode(text)

    def decode(self, ids):
        return self.sp.decode(ids)

    def vocab_size(self):
        return self.sp.get_piece_size()


# =========================
# ROPE
# =========================
def rope(x):
    B, T, H, D = x.shape
    half = D // 2

    freqs = torch.arange(half, device=x.device) / half
    freqs = 1.0 / (10000 ** freqs)

    t = torch.arange(T, device=x.device)
    angles = torch.outer(t, freqs)

    cos = torch.cos(angles)
    sin = torch.sin(angles)

    x1, x2 = x[..., :half], x[..., half:]
    return torch.cat([x1*cos - x2*sin, x1*sin + x2*cos], dim=-1)


# =========================
# PAGED KV CACHE (vLLM style simplified)
# =========================
class KVCache:
    def __init__(self, layers, heads, dim, max_tokens=4096):
        self.layers = layers
        self.heads = heads
        self.dim = dim
        self.max_tokens = max_tokens
        self.device = None
        
        self.reset()

    def reset(self):
        self.k = None
        self.v = None
        self.ptr = 0

    def append(self, layer, k, v):
        """Append k,v for a layer (k,v should be [1, heads, dim] or [batch, heads, dim])"""
        if self.device is None:
            self.device = k.device
            
        if self.k is None:
            # Initialize on first append
            batch_size = k.shape[0]
            self.k = torch.zeros(self.layers, batch_size, self.max_tokens, self.heads, self.dim, device=self.device)
            self.v = torch.zeros(self.layers, batch_size, self.max_tokens, self.heads, self.dim, device=self.device)
        
        # Store only the latest tokens
        self.k[layer, :, self.ptr] = k
        self.v[layer, :, self.ptr] = v

    def get(self, layer):
        """Get all cached k,v for a layer"""
        if self.k is None:
            return None, None
        return self.k[layer, :, :self.ptr], self.v[layer, :, :self.ptr]

    def advance_ptr(self):
        """Move pointer forward"""
        self.ptr += 1
        if self.ptr >= self.max_tokens:
            self.ptr = self.max_tokens - 1


# =========================
# TENSOR PARALLEL LINEAR
# =========================
class TPLinear(nn.Module):
    def __init__(self, in_f, out_f):
        super().__init__()
        self.rank = torch.cuda.current_device() if torch.cuda.is_available() else 0
        self.world = Config.tp_size

        shard = out_f // self.world

        self.weight = nn.Parameter(torch.randn(shard, in_f) * 0.02)

    def forward(self, x):
        out = F.linear(x, self.weight)
        return out


# =========================
# ATTENTION
# =========================
class Attention(nn.Module):
    def __init__(self, cfg, layer_id):
        super().__init__()
        self.h = cfg.heads
        self.d = cfg.dim // cfg.heads
        self.layer_id = layer_id
        self.dim = cfg.dim

        self.q_proj = TPLinear(cfg.dim, cfg.dim)
        self.k_proj = TPLinear(cfg.dim, cfg.dim)
        self.v_proj = TPLinear(cfg.dim, cfg.dim)
        self.o_proj = TPLinear(cfg.dim, cfg.dim)

    def forward(self, x, cache=None, use_cache=False):
        B, T, C = x.shape

        # Project to q, k, v
        q = self.q_proj(x).view(B, T, self.h, self.d).transpose(1, 2)  # [B, heads, T, d]
        k = self.k_proj(x).view(B, T, self.h, self.d).transpose(1, 2)  # [B, heads, T, d]
        v = self.v_proj(x).view(B, T, self.h, self.d).transpose(1, 2)  # [B, heads, T, d]

        # Apply RoPE
        q = rope(q)
        k = rope(k)

        # Use cache if provided (for generation)
        if cache is not None and use_cache:
            cache.append(self.layer_id, k, v)
            k_cache, v_cache = cache.get(self.layer_id)
            if k_cache is not None:
                k = k_cache
                v = v_cache

        # Attention
        att = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        att = att.transpose(1, 2).contiguous().view(B, T, C)
        
        return self.o_proj(att)


# =========================
# BLOCK
# =========================
class Block(nn.Module):
    def __init__(self, cfg, i):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.dim)
        self.attn = Attention(cfg, i)
        self.ln2 = nn.LayerNorm(cfg.dim)

        self.ff = nn.Sequential(
            TPLinear(cfg.dim, 4*cfg.dim),
            nn.SiLU(),
            TPLinear(4*cfg.dim, cfg.dim)
        )

    def forward(self, x, cache=None, use_cache=False):
        x = x + self.attn(self.ln1(x), cache=cache, use_cache=use_cache)
        x = x + self.ff(self.ln2(x))
        return x


# =========================
# MODEL
# =========================
class LLM(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.embed = nn.Embedding(cfg.vocab_size, cfg.dim)
        self.blocks = nn.ModuleList([Block(cfg, i) for i in range(cfg.layers)])
        self.norm = nn.LayerNorm(cfg.dim)
        self.head = nn.Linear(cfg.dim, cfg.vocab_size)

    def forward(self, x, cache=None, use_cache=False):
        x = self.embed(x)

        for b in self.blocks:
            x = b(x, cache=cache, use_cache=use_cache)

        return self.head(self.norm(x))


# =========================
# GENERATION
# =========================
def generate(model, tokenizer, prompt, max_new_tokens=100, temperature=1.0):
    """Generate text from a prompt"""
    model.eval()
    
    # Initialize cache
    cache = KVCache(model.cfg.layers, model.cfg.heads, model.cfg.dim // model.cfg.heads)
    
    # Encode prompt
    input_ids = tokenizer.encode(prompt)
    x = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(model.cfg.device)
    
    generated = input_ids.copy()
    
    with torch.no_grad():
        for _ in range(max_new_tokens):
            logits = model(x, cache=cache, use_cache=True)
            next_logits = logits[:, -1, :] / temperature
            
            probs = F.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            generated.append(next_token.item())
            
            # Only pass the new token for next iteration (KV cache is used)
            x = next_token.unsqueeze(0)
            cache.advance_ptr()
    
    return tokenizer.decode(generated)


def speculative(model, draft_model, x):
    """Speculative decoding (simplified)"""
    with torch.no_grad():
        draft = draft_model(x[:, -1:])
        target = model(x[:, -1:])

    if torch.argmax(draft) == torch.argmax(target):
        return draft
    return target


# =========================
# TRAINING & EVALUATION
# =========================
def train_step(model, data_iter, cfg, optimizer, scaler, step):
    """Single training step"""
    model.train()
    
    x, y = next(data_iter)
    x, y = x.to(cfg.device), y.to(cfg.device)

    with torch.cuda.amp.autocast():
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))

    optimizer.zero_grad()
    scaler.scale(loss).backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(optimizer)
    scaler.update()
    
    return loss.item()


def evaluate(model, val_data, cfg, max_batches=10):
    """Evaluate on validation set"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for i, (x, y) in enumerate(val_data):
            if i >= max_batches:
                break
            x, y = x.to(cfg.device), y.to(cfg.device)
            logits = model(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))
            total_loss += loss.item()
    
    return total_loss / max(1, min(i+1, max_batches))


def train(model, train_data, val_data, cfg, tokenizer=None):
    """Full training loop"""
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=0.1)
    scaler = torch.cuda.amp.GradScaler() if torch.cuda.is_available() else None
    
    # Warmup schedule
    def get_lr(step):
        if step < cfg.warmup_steps:
            return cfg.lr * (step / cfg.warmup_steps)
        return cfg.lr
    
    step = 0
    best_val_loss = float('inf')
    
    print(f"Starting training on {cfg.device}...")
    print(f"Model params: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")
    
    while step < cfg.max_steps:
        try:
            for x, y in train_data:
                if step >= cfg.max_steps:
                    break
                
                # Update learning rate
                for param_group in optimizer.param_groups:
                    param_group['lr'] = get_lr(step)
                
                # Training step
                loss = train_step(model, iter([(x, y)]), cfg, optimizer, scaler, step)
                
                # Logging
                if step % 100 == 0:
                    print(f"Step {step:5d} | Loss: {loss:.4f} | LR: {get_lr(step):.6f}")
                
                # Validation
                if step % cfg.save_interval == 0 and step > 0:
                    val_loss = evaluate(model, val_data, cfg)
                    print(f"  Val Loss: {val_loss:.4f}")
                    
                    # Save checkpoint
                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        checkpoint = {
                            'step': step,
                            'model': model.state_dict(),
                            'optimizer': optimizer.state_dict(),
                            'config': cfg.__dict__,
                            'val_loss': val_loss
                        }
                        path = os.path.join(cfg.checkpoint_dir, f'model_step_{step}.pt')
                        torch.save(checkpoint, path)
                        print(f"  Saved checkpoint to {path}")
                
                step += 1
        except StopIteration:
            break
    
    print("Training complete!")
    return model


# =========================
# SAVING & LOADING
# =========================
def save_model(model, path="model.pt"):
    """Save model checkpoint"""
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")


def load_model(model, path="model.pt"):
    """Load model checkpoint"""
    model.load_state_dict(torch.load(path))
    print(f"Model loaded from {path}")
    return model


def export_gguf(model, path="model.gguf"):
    """Export model to GGUF format (requires gguf library)"""
    try:
        import gguf
    except ImportError:
        print("GGUF export requires: pip install gguf")
        return
    
    w = gguf.GGUFWriter(path, "llama-hybrid")
    
    for k, v in model.state_dict().items():
        w.add_tensor(k, v.detach().cpu().numpy())
    
    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()
    print(f"Model exported to {path}")


# =========================
# INTERACTIVE CHAT
# =========================
def chat(model, tokenizer, cfg):
    """Interactive chat with the model"""
    if tokenizer is None:
        print("Tokenizer required for chat mode")
        return
    
    model.eval()
    model.to(cfg.device)
    
    print("Chat mode (type 'quit' to exit):")
    
    while True:
        try:
            prompt = input(">>> ")
            if prompt.lower() == 'quit':
                break
            
            response = generate(model, tokenizer, prompt, max_new_tokens=100)
            print(f"AI: {response}\n")
        except KeyboardInterrupt:
            break
    
    print("Chat ended.")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    cfg = Config()
    
    print("=" * 50)
    print("LLM Training from Scratch")
    print("=" * 50)
    print(f"Config:")
    for k, v in cfg.__dict__.items():
        print(f"  {k}: {v}")
    print()