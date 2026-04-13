"""Gratify LLM Package."""

from .config import GratifyConfig, SYSTEM_BRAND
from .model import GratifyLLM
from .gpu_utils import detect_gpu, setup_gpu_if_available

__version__ = "0.1.0"
__author__ = "sirco"
__all__ = [
    "GratifyConfig",
    "GratifyLLM",
    "detect_gpu",
    "setup_gpu_if_available",
    "SYSTEM_BRAND",
]
