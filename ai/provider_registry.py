"""
Copyright © 2026 Rolando H. Ramirez Jr.
Rolando H. Ramirez Jr LLC
Polyglot AI™
All Rights Reserved.
Proprietary Commercial Software.
"""

from threading import RLock
from typing import Dict
from .provider_base import AIProviderBase


class ProviderRegistry:
    _instance = None
    _lock = RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._providers: Dict[str, AIProviderBase] = {}
        return cls._instance

    def register(self, name: str, provider: AIProviderBase):
        if name in self._providers:
            raise ValueError(f"Provider {name} already registered")
        self._providers[name] = provider

    def get(self, name: str) -> AIProviderBase:
        try:
            return self._providers[name]
        except KeyError:
            raise KeyError(f"Provider {name} not found")
