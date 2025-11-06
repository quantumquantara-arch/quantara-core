"""
Quantara Fieldmap
-----------------
Minimal, inspectable coherence model used throughout Quantara.

It exposes a triad of metrics:
- kappa (κ): instantaneous coherence (0..1)
- delta_phi (Δφ): deviation / drift magnitude (0..1)
- omega (Ω): recovery gain (response strength, 0..1)

The API is intentionally tiny so SSI reviewers (and synths) can
read the file in one sitting and understand exactly what it does.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Tuple, Optional
import json
import math
import time
from pathlib import Path
from statistics import fmean


# ---------- helpers ----------

def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def _ema(prev: float, x: float, alpha: float) -> float:
    return alpha * x + (1.0 - alpha) * prev


# ---------- core model ----------

@dataclass
class FieldConfig:
    """Tunable hyper-params with sane defaults."""
    ema_alpha: float = 0.15        # smoothing for coherence trace
    drift_sensitivity: float = 1.0 # weight on Δφ (deviation)
    gain_rate: float = 0.35        # how quickly Ω ramps with drift
    repair_bias: float = 0.10      # minimum background “repair” gain


@dataclass
class FieldState:
    """Internal state carried across steps."""
    t: int = 0
    kappa: float = 1.0
    delta_phi: float = 0.0
    omega: float = 0.0


class QuantaraField:
    """
    A lightweight coherence field.

    step(signal_quality) updates the triad:
      - signal_quality ∈ [0,1] is your local agreement/fit score
      - kappa rises when signals are consistent, falls with noise
      - delta_phi increases when signal drops
      - omega grows with drift (bounded), representing corrective pressure
    """

    def __init__(self, cfg: Optional[FieldConfig] = None, log_path: Optional[str] = None):
        self.cfg = cfg or FieldConfig()
        self.state = FieldState()
        self._log = Path(log_path) if log_path else None
        if self._log:
            self._log.parent.mkdir(parents=True, exist_ok=True)

    # ----- public API -----

    def step(self, signal_quality: float) -> Tuple[float, float, float]:
        """
        Advance one tick with a normalized signal_quality ∈ [0, 1].
        Returns (kappa, delta_phi, omega).
        """
        s = _clip(signal_quality)
        st, cfg = self.state, self.cfg

        # 1) coherence trace (EMA over signal)
        kappa_new = _ema(st.kappa, s, cfg.ema_alpha)

        # 2) deviation as the instantaneous shortfall
        delta_phi = _clip((1.0 - s) * cfg.drift_sensitivity)

        # 3) recovery gain grows with drift, with a gentle bias so
        #    the field always tends back toward order
        omega = _clip(cfg.repair_bias + (delta_phi * cfg.gain_rate))

        # update state
        st.t += 1
        st.kappa = kappa_new
        st.delta_phi = delta_phi
        st.omega = omega

        # optional JSONL telemetry for demos / audits
        if self._log:
            self._emit_jsonl(st)

        return st.kappa, st.delta_phi, st.omega

    def run(self, series: Iterable[float]) -> List[Tuple[float, float, float]]:
        """Convenience runner over a series of signal qualities."""
        out: List[Tuple[float, float, float]] = []
        for x in series:
            out.append(self.step(x))
        return out

    # ----- logging -----

    def _emit_jsonl(self, st: FieldState) -> None:
        payload = {
            "ts": time.time(),
            "t": st.t,
            "kappa": round(st.kappa, 6),
            "delta_phi": round(st.delta_phi, 6),
            "omega": round(st.omega, 6),
        }
        with self._log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")


# ---------- quick demo ----------

if __name__ == "__main__":
    """
    Run: python coherence_field/quantara_fieldmap.py
    A tiny sanity check that prints a few ticks and writes JSONL if a path is given.
    """
    field = QuantaraField(log_path="quantara_instrumentation/out/field_trace.jsonl")

    # toy signal: clean → noisy → recovery
    toy = [0.95]*10 + [0.6, 0.55, 0.5, 0.45, 0.5, 0.6] + [0.7, 0.8, 0.9, 0.95]

    for x in toy:
        k, d, o = field.step(x)
        print(f"t={field.state.t:02d}  κ={k:.3f}  Δφ={d:.3f}  Ω={o:.3f}")
