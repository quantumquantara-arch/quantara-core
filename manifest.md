# Quantara Core — Manifest & Initialization

A unified manifest and initialization layer for the Quantara Core repository.

---

## Purpose

Quantara Core is the foundational codebase for coherence-based intelligence: bridging perception (π), harmonic integration (φ), and expansion (e). It enables self-monitoring, coherence evaluation, and ethical evolution from AGI → CI → ASI.

---

## Repository Map

---

## Initialization Code (all in one block)

```python
# =========================
# src/quantara_core/__init__.py
# =========================
"""
Quantara Core Initialization

This file exposes the main API for coherence-based intelligence modules.
"""

from .metacognition_layer import awaken, SelfMonitor

__all__ = ["awaken", "SelfMonitor"]

# =========================
# src/quantara_core/coherence_field/__init__.py
# =========================
"""
Coherence Field Initialization

Defines the primary interfaces for coherence scoring and mapping.
"""

from .llm_coherence_score import score_text, CoherenceField
from .fieldmap_quantara import FIELD_MAP

__all__ = ["score_text", "CoherenceField", "FIELD_MAP"]

pip install -r requirements.txt
python - <<'PY'
from quantara_core import awaken
from quantara_core.coherence_field import score_text

state = awaken("Observe → integrate → expand.", return_state=True)
print(state['phase'], score_text("The system learns to align and expand."))
PY
