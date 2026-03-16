import os
import random
from typing import List, Dict, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

class KeyManager:
    """
    Manages API keys for multiple providers with rotation and failure handling.
    """
    def __init__(self):
        self.keys = {
            "gemini": config.GEMINI_API_KEYS,
            "openai": config.OPENAI_API_KEYS,
            "anthropic": config.ANTHROPIC_API_KEYS
        }
        self.current_index = {
            "gemini": 0,
            "openai": 0,
            "anthropic": 0
        }
        self.failed_keys = {
            "gemini": set(),
            "openai": set(),
            "anthropic": set()
        }

    def get_key(self, provider: str = "gemini") -> Optional[str]:
        """Returns the next available key for the provider."""
        if provider not in self.keys or not self.keys[provider]:
            return None

        available_keys = [k for k in self.keys[provider] if k not in self.failed_keys[provider]]
        
        if not available_keys:
            # If all failed, reset failed list (naive reset)
            print(f"All keys for {provider} failed. Resetting pool.")
            self.failed_keys[provider] = set()
            available_keys = self.keys[provider]

        # Round robin
        key = available_keys[self.current_index[provider] % len(available_keys)]
        self.current_index[provider] += 1
        return key

    def report_failure(self, provider: str, key: str):
        """Marks a key as failed (e.g., 429 Rate Limit)."""
        if provider in self.failed_keys:
            self.failed_keys[provider].add(key)
            print(f"Key {key[:4]}... for {provider} marked as failed.")

    def add_key(self, provider: str, key: str):
        """Dynamically adds a key."""
        if provider in self.keys:
            self.keys[provider].append(key)
