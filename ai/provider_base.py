"""
Copyright © 2026 Rolando H. Ramirez Jr.
Rolando H. Ramirez Jr LLC
Polyglot AI™
All Rights Reserved.
Proprietary Commercial Software.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, AsyncGenerator


class AIProviderBase(ABC):
    """Abstract base for all model adapters."""

    @abstractmethod
    async def generate(self, prompt: str, *, metadata: Dict[str, Any] | None = None) -> str:
        """Return a complete response."""

    @abstractmethod
    def generate_stream(
        self, prompt: str, *, metadata: Dict[str, Any] | None = None
    ) -> AsyncGenerator[str, None]:
        """Yield partial tokens for streaming use-cases."""
