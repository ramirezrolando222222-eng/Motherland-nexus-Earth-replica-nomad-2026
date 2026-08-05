"""
Copyright © 2026 Rolando H. Ramirez Jr.
Rolando H. Ramirez Jr LLC
Polyglot AI™
All Rights Reserved.
Proprietary Commercial Software.
"""

from typing import Any, Dict, AsyncGenerator
import logging

from ai.provider_base import AIProviderBase
from ai.provider_registry import ProviderRegistry

logger = logging.getLogger(__name__)


class Orchestrator:
    """High-level entry point for all AI interactions."""

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    async def generate(
        self,
        provider_name: str,
        prompt: str,
        *,
        stream: bool = False,
        metadata: Dict[str, Any] | None = None,
    ) -> AsyncGenerator[str, None] | str:
        """Route a prompt to the selected provider.

        If stream is False returns a string. If True returns an async generator.
        """
        provider: AIProviderBase = self.registry.get(provider_name)
        logger.debug("Orchestrator dispatching to %s (stream=%s)", provider_name, stream)
        if stream:
            return provider.generate_stream(prompt, metadata=metadata)
        else:
            return await provider.generate(prompt, metadata=metadata)
