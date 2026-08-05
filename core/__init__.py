"""
Copyright © 2026 Rolando H. Ramirez Jr.
Rolando H. Ramirez Jr LLC
Polyglot AI™
All Rights Reserved.
Proprietary Commercial Software.
"""

from .provider_registry import ProviderRegistry

# Lazy import adapters to avoid import-time side effects in CI/tests
try:
    from .gemini_adapter import GeminiAdapter  # type: ignore
except Exception:
    GeminiAdapter = None

registry = ProviderRegistry()
if GeminiAdapter is not None:
    try:
        registry.register("gemini", GeminiAdapter())
    except Exception:
        # registration is best-effort for the scaffold
        pass
