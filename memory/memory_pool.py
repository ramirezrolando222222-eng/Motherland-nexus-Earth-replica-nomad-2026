"""
Copyright © 2026 Rolando H. Ramirez Jr.
Rolando H. Ramirez Jr LLC
Polyglot AI™
All Rights Reserved.
Proprietary Commercial Software.
"""

import threading
from typing import Dict, List, Tuple
from collections import defaultdict

# The real NexusMemoryPool is provided by the Motherland Nexus package.
try:
    from motherland_nexus import VenomMemoryPool as NexusMemoryPool  # type: ignore
except Exception:
    NexusMemoryPool = None


class VenomMemoryPool:
    """Thin wrapper around Motherland Nexus' VenomMemoryPool.

    Provides an in-memory conversation store for the scaffold.
    """

    def __init__(self, ttl_seconds: int = 86400):
        self._nexus = NexusMemoryPool() if NexusMemoryPool is not None else None
        self._conversations: defaultdict[str, List[Tuple[str, str]]] = defaultdict(list)
        self._lock = threading.RLock()
        self.ttl = ttl_seconds

    def store_conversation(self, conv_id: str, user_msg: str, ai_msg: str):
        with self._lock:
            self._conversations[conv_id].append((user_msg, ai_msg))
            # If Nexus pool exists, inform it (best-effort)
            if self._nexus is not None:
                try:
                    self._nexus.allocate(len(user_msg) + len(ai_msg))
                except Exception:
                    pass

    def get_conversation(self, conv_id: str) -> str:
        with self._lock:
            turns = self._conversations.get(conv_id, [])
            return "\n".join([f"User: {u}\nAI: {a}" for u, a in turns])

    def append_turn(self, conv_id: str, user_msg: str, ai_msg: str):
        self.store_conversation(conv_id, user_msg, ai_msg)
