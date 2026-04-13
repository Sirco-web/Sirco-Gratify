"""Model architecture for Gratify LLM."""

import torch
import torch.nn as nn
import math


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    
    def __init__(self, embedding_dim, max_seq_length=512):
        super().__init__()
        self.embedding_dim = embedding_dim
        
        # Create positional encodings
        pe = torch.zeros(max_seq_length, embedding_dim)
        position = torch.arange(0, max_seq_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embedding_dim, 2).float() * 
            -(math.log(10000.0) / embedding_dim)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        if embedding_dim % 2 == 1:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        else:
            pe[:, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer("pe", pe.unsqueeze(0))
    
    def forward(self, x):
        """Add positional encoding to embeddings."""
        return x + self.pe[:, :x.size(1), :].to(x.device)


class TransformerBlock(nn.Module):
    """Single transformer encoder block."""
    
    def __init__(self, embedding_dim, num_heads, hidden_dim, dropout=0.1):
        super().__init__()
        
        # Multi-head attention
        self.attention = nn.MultiheadAttention(
            embedding_dim, num_heads, dropout=dropout, batch_first=True
        )
        
        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim),
            nn.Dropout(dropout),
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        """Forward pass with residual connections."""
        # Self-attention with residual
        attn_out, _ = self.attention(x, x, x, attn_mask=mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # Feed-forward with residual
        ff_out = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_out))
        
        return x


class GratifyLLM(nn.Module):
    """Gratify Language Model."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Embeddings
        self.embedding = nn.Embedding(config.vocab_size, config.embedding_dim)
        self.pos_encoding = PositionalEncoding(config.embedding_dim, config.max_seq_length)
        self.embedding_dropout = nn.Dropout(config.dropout)
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerBlock(
                config.embedding_dim,
                config.num_heads,
                config.hidden_dim,
                config.dropout
            )
            for _ in range(config.num_layers)
        ])
        
        # Output layer
        self.norm = nn.LayerNorm(config.embedding_dim)
        self.output = nn.Linear(config.embedding_dim, config.vocab_size)
    
    def forward(self, input_ids, mask=None):
        """Forward pass."""
        # Embed input
        x = self.embedding(input_ids)
        x = self.pos_encoding(x)
        x = self.embedding_dropout(x)
        
        # Apply transformer layers
        for layer in self.layers:
            x = layer(x, mask=mask)
        
        # Final layer norm and output
        x = self.norm(x)
        logits = self.output(x)
        
        return logits
    
    def generate(self, prompt_ids, max_new_tokens=50, device="cpu", temperature=0.7):
        """Generate text from a prompt."""
        self.eval()
        current_ids = prompt_ids.clone().to(device)
        
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Forward pass
                logits = self(current_ids)
                next_logits = logits[:, -1, :] / temperature
                
                # Sample next token
                probs = torch.softmax(next_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append to sequence
                current_ids = torch.cat([current_ids, next_token], dim=1)
                
                # Keep only last max_seq_length tokens
                if current_ids.shape[1] > self.config.max_seq_length:
                    current_ids = current_ids[:, -self.config.max_seq_length:]
        
        self.train()
        return current_ids
    
    def count_parameters(self):
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
