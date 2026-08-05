"""
Copyright © 2026 Rolando H. Ramirez Jr.
Rolando H. Ramirez Jr LLC
Polyglot AI™
All Rights Reserved.
Proprietary Commercial Software.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from memory.memory_pool import VenomMemoryPool


@dataclass
class Agent:
    """Represents a single conversational entity."""
    agent_id: str
    memory: VenomMemoryPool = field(default_factory=VenomMemoryPool)
    state: Dict[str, Any] = field(default_factory=dict)

    async def handle(self, prompt: str, orchestrator, provider: str = "gemini") -> str:
        # Retrieve prior context
        history = self.memory.get_conversation(self.agent_id)
        enriched_prompt = f"{history}\nUser: {prompt}"
        response = await orchestrator.generate(
            provider, enriched_prompt, metadata={"conversation_id": self.agent_id}
        )
        # Store new turn
        self.memory.append_turn(self.agent_id, prompt, response)
        return response
