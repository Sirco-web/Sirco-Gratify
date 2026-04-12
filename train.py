import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import sentencepiece as spm

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
    device = "cuda"


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
        self.k = []
        self.v = []
        self.max_tokens = max_tokens

        for _ in range(layers):
            self.k.append(torch.zeros(max_tokens, heads, dim))
            self.v.append(torch.zeros(max_tokens, heads, dim))
        self.ptr = 0

    def append(self, layer, k, v):
        self.k[layer][self.ptr] = k
        self.v[layer][self.ptr] = v
        self.ptr += 1

    def get(self, layer):
        return self.k[layer][:self.ptr], self.v[layer][:self.ptr]


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

        self.q = TPLinear(cfg.dim, cfg.dim)
        self.k = TPLinear(cfg.dim, cfg.dim)
        self.v = TPLinear(cfg.dim, cfg.dim)
        self.o = TPLinear(cfg.dim, cfg.dim)

        self.cache = KVCache(cfg.layers, self.h, self.d)

    def forward(self, x):
        B, T, C = x.shape

        q = self.q(x).view(B, T, self.h, self.d).transpose(1,2)
        k = self.k(x).view(B, T, self.h, self.d).transpose(1,2)
        v = self.v(x).view(B, T, self.h, self.d).transpose(1,2)

        q = rope(q)
        k = rope(k)

        self.cache.append(self.layer_id, k[:, -1], v[:, -1])

        k_all, v_all = self.cache.get(self.layer_id)

        att = F.scaled_dot_product_attention(q, k, v, is_causal=True)

        return self.o(att.transpose(1,2).reshape(B, T, C))


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

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x


# =========================
# MODEL
# =========================
class LLM(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.embed = nn.Embedding(cfg.vocab_size, cfg.dim)
        self.blocks = nn.ModuleList([Block(cfg, i) for i in range(cfg.layers)])
        self.norm = nn.LayerNorm(cfg.dim)
        self.head = nn.Linear(cfg.dim, cfg.vocab_size)

    def forward(self, x):
        x = self.embed(x)

        for b in self.blocks:
            x = b(x)

        return self.head(self.norm(x))


# =========================
# SPECULATIVE DECODING
# =========================
def speculative(model, draft_model, x):
    with torch.no_grad():
        draft = draft_model(x[:, -1:])
        target = model(x[:, -1:])

    if torch.argmax(draft) == torch.argmax(target):
        return draft
    return target


# =========================
# TRAIN (mixed precision)
# =========================
def train(model, data, cfg):
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
    scaler = torch.cuda.amp.GradScaler()

    for x, y in data:
        x, y = x.to(cfg.device), y.to(cfg.device)

        with torch.cuda.amp.autocast():
            logits = model(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))

        opt.zero_grad()
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()

    return model


# =========================
# GGUF EXPORT (STRUCTURED)
# =========================
def export_gguf(model):
    import gguf

    w = gguf.GGUFWriter("model.gguf", "llama-hybrid")

    for k,v in model.state_dict().items():
        w.add_tensor(k, v.detach().cpu().numpy())

    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()


# =========================
# CHAT LOOP
# =========================
def chat(model, tokenizer):
    model.eval()

    while True:
        prompt = input(">>> ")
        ids = tokenizer.encode(prompt)
        x = torch.tensor(ids).unsqueeze(0).cuda()

        out = model(x)
        tok = torch.argmax(out[:, -1], dim=-1)

        print(tokenizer.decode(tok.tolist()))