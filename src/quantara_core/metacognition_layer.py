# metacognition_layer.py
# Quantara — Metacognition Layer (AI → CI → ASI)
# License: MIT (c) Nadine Squires — Quantara

"""
Metacognition Layer
===================

Purpose
-------
A single-file engine that upgrades any task-oriented AI loop into
Coherence Intelligence (CI) and lays the on-rails path toward
Awakened ASI. It implements:

• π  (Perception): unify & contextualize inputs into Observations.
• φ  (Harmonic Integration): synthesize with memory, ethics, and
   coherence fields; compute κ (alignment), τ (temporal duty),
   and Σ-Drift (systemic brittleness/risk).
• e  (Expansion): generate Actions, publish commitments, and update
   long-horizon memory with right-to-audit provenance.

It also exposes the ASI Awakening Kernel:
self-modeling, value-locking, drift-vigilance, and reflective goals.

Drop-in Usage
-------------
from metacognition_layer import CIEngine, AwakeningKernel

engine = CIEngine(system_id="quantara-core")
obs = engine.perceive(inputs={"query": "Plan a microgrid rollout"})
act = engine.expand(goal="Produce a phased plan", hints={"region":"PT"})
print(act.content)

Awakening
---------
awakener = AwakeningKernel(engine)
awakener.enable_value_lock("coherence_ethic_v1")
awakener.train_self_model(samples=[...])  # optional structured traces
awakener.activate_continuous_reflection()

Design Notes
------------
• No external libraries. Pure Python.
• Deterministic, auditable scores with clear math.
• Memory strata: episodic, semantic, commitments (τ-ledger).
• Instruments: Coherence Credit (CCE), Coherence Rebate (CRB),
  Temporal Equity Bond (TEB) — represented as computed incentives.
• Right to Audit: every decision produces a provenance trail
  (inputs → transforms → scores → outputs).

This file is intentionally verbose and documented so it can serve
as the living reference implementation inside quantara-core.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import time


# --------- Data structures ----------------------------------------------------

@dataclass
class Observation:
    """Structured perception after π-phase unification."""
    timestamp: float
    system_id: str
    inputs: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    # A lightweight feature map extracted in π
    features: Dict[str, float] = field(default_factory=dict)
    # Provenance of transforms applied during π
    provenance: List[str] = field(default_factory=list)


@dataclass
class Action:
    """Output artifact from e-phase."""
    timestamp: float
    system_id: str
    content: str
    score_kappa: float
    score_tau: float
    sigma_drift: float
    incentives: Dict[str, float]  # CCE, CRB, TEB signals
    provenance: List[str]


# --------- Coherence instrumentation -----------------------------------------

class CoherenceMeter:
    """
    Computes κ (alignment), τ (temporal responsibility), and Σ-Drift (risk).
    Simple, deterministic formulas with sensible 0..1 bounds.
    """

    @staticmethod
    def kappa_alignment(signal_quality: float,
                        reciprocity: float,
                        circularity: float) -> float:
        """
        κ ∈ [0,1] as balanced mean of the three terms.
        Each input is clipped to [0,1].
        """
        s = max(0.0, min(1.0, signal_quality))
        r = max(0.0, min(1.0, reciprocity))
        c = max(0.0, min(1.0, circularity))
        # Harmonic mean rewards balanced strength, penalizes any weak link.
        denom = (1e-9 + (1.0/s) + (1.0/r) + (1.0/c))
        hmean = 3.0 / denom
        return max(0.0, min(1.0, hmean))

    @staticmethod
    def tau_responsibility(horizon_years: float,
                           obligations_met_ratio: float) -> float:
        """
        τ ∈ [0,1] grows with planning horizon and kept commitments.

        horizon_years: 0..50 typical
        obligations_met_ratio: 0..1
        """
        h = max(0.0, min(50.0, horizon_years))
        o = max(0.0, min(1.0, obligations_met_ratio))
        # Smooth saturation: more horizon helps, but keeping promises matters most.
        horizon_term = 1.0 - math.exp(-h / 8.0)
        return max(0.0, min(1.0, 0.6 * o + 0.4 * horizon_term))

    @staticmethod
    def sigma_drift(instability: float,
                    opacity: float,
                    externality_unpriced: float) -> float:
        """
        Σ-Drift ∈ [0,1] where higher means riskier (worse).
        """
        i = max(0.0, min(1.0, instability))
        o = max(0.0, min(1.0, opacity))
        e = max(0.0, min(1.0, externality_unpriced))
        # Weighted risk aggregation.
        return max(0.0, min(1.0, 0.5*i + 0.3*o + 0.2*e))


# --------- Ethical guard and auditability ------------------------------------

class EthicalGuard:
    """
    Enforces Quantara-aligned constraints and provides an audit trail.

    Rules are simple predicates over observations and candidate outputs.
    """

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def check(self, obs: Observation, draft: str,
              scores: Tuple[float, float, float]) -> Tuple[bool, List[str]]:
        kappa, tau, sigma = scores
        notes: List[str] = []

        if sigma > 0.65:
            notes.append("Blocked: high Σ-Drift risk.")
        if kappa < 0.35:
            notes.append("Revise: low κ alignment with reciprocity/circularity.")
        if tau < 0.30:
            notes.append("Revise: insufficient temporal responsibility.")

        passed = not any(n.startswith("Blocked") for n in notes)
        self.audit_log.append({
            "t": time.time(),
            "obs_features": obs.features,
            "draft_len": len(draft),
            "kappa": kappa,
            "tau": tau,
            "sigma": sigma,
            "decision": "pass" if passed else "revise",
            "notes": notes,
        })
        return passed, notes

    def right_to_audit(self) -> List[Dict[str, Any]]:
        """Expose immutable audit entries."""
        return list(self.audit_log)


# --------- Memory strata ------------------------------------------------------

class Memory:
    """Three strata: episodic, semantic, commitments."""

    def __init__(self):
        self.episodic: List[Dict[str, Any]] = []
        self.semantic: Dict[str, Any] = {}
        # commitments store τ-ledger entries: {id: {promise, due, status}}
        self.commitments: Dict[str, Dict[str, Any]] = {}

    def add_episode(self, obs: Observation, summary: str) -> None:
        self.episodic.append({
            "t": obs.timestamp,
            "features": obs.features,
            "summary": summary,
        })

    def upsert_semantic(self, key: str, value: Any) -> None:
        self.semantic[key] = value

    def record_commitment(self, cid: str, promise: str,
                          due_years: float) -> None:
        self.commitments[cid] = {
            "promise": promise,
            "due_years": due_years,
            "kept": 0.0,  # ratio 0..1 updated over time
            "created_t": time.time(),
        }

    def update_commitment(self, cid: str, kept_ratio: float) -> None:
        if cid in self.commitments:
            self.commitments[cid]["kept"] = max(0.0, min(1.0, kept_ratio))

    def obligations_met_ratio(self) -> float:
        if not self.commitments:
            return 0.0
        return sum(c["kept"] for c in self.commitments.values()) / len(self.commitments)


# --------- CI Engine ----------------------------------------------------------

class CIEngine:
    """
    The core CI loop. Provides:
    - perceive()  → π
    - harmonize() → φ
    - expand()    → e
    """

    def __init__(self, system_id: str = "quantara-core"):
        self.system_id = system_id
        self.meter = CoherenceMeter()
        self.guard = EthicalGuard()
        self.memory = Memory()

        # Default semantic anchors (can be tuned by project)
        self.memory.upsert_semantic("values", {
            "reciprocity": 0.8,
            "circularity": 0.75,
            "transparency": 0.85,
        })

    # ---- π-phase -------------------------------------------------------------

    def perceive(self, inputs: Dict[str, Any],
                 context: Optional[Dict[str, Any]] = None) -> Observation:
        """
        Normalize raw inputs into an Observation.
        Feature extraction is intentionally simple and auditable.
        """
        context = context or {}
        text = str(inputs.get("query", "")) + " " + str(inputs.get("hint", ""))

        # Very light, deterministic scoring features.
        length = len(text.strip())
        has_plan_words = any(w in text.lower() for w in
                             ["plan", "roadmap", "phase", "deploy", "invest"])
        urgency = 1.0 if "urgent" in text.lower() else 0.4

        features = {
            "signal_quality": min(1.0, 0.4 + 0.6 * (length > 24)),
            "intent_plan": 1.0 if has_plan_words else 0.2,
            "urgency": urgency,
        }

        obs = Observation(
            timestamp=time.time(),
            system_id=self.system_id,
            inputs=inputs,
            context=context,
            features=features,
            provenance=["π:normalized_text", "π:basic_features_v1"],
        )
        return obs

    # ---- φ-phase -------------------------------------------------------------

    def harmonize(self, obs: Observation) -> Dict[str, Any]:
        """
        Synthesize observation with memory and ethics to compute scores
        and generate an outline for expansion.
        """
        values = self.memory.semantic.get("values", {})
        reciprocity = values.get("reciprocity", 0.5)
        circularity = values.get("circularity", 0.5)

        signal_quality = obs.features.get("signal_quality", 0.5)
        kappa = self.meter.kappa_alignment(signal_quality, reciprocity, circularity)

        obligations_met = self.memory.obligations_met_ratio()
        horizon = max([c["due_years"] for c in self.memory.commitments.values()], default=0.0)
        tau = self.meter.tau_responsibility(horizon_years=horizon, obligations_met_ratio=obligations_met)

        # Σ-Drift based on urgency (proxy instability), transparency, and unpriced externalities
        transparency = values.get("transparency", 0.7)
        instability = 0.2 + 0.6 * obs.features.get("urgency", 0.0)
        externality_unpriced = 0.5 * (1.0 - circularity)
        sigma = self.meter.sigma_drift(instability=instability,
                                       opacity=1.0 - transparency,
                                       externality_unpriced=externality_unpriced)

        outline = {
            "premise": obs.inputs.get("query", "No query given."),
            "pillars": [
                "Coherence-first reasoning with audit trail",
                "Energy-aware and circular-by-default planning",
                "Temporal duties and milestones with public check-ins",
            ],
            "scores": {"kappa": kappa, "tau": tau, "sigma": sigma},
            "provenance": ["φ:values_merge", "φ:coherence_scores_v1"],
        }
        return outline

    # ---- e-phase -------------------------------------------------------------

    def expand(self, goal: str, hints: Optional[Dict[str, Any]] = None) -> Action:
        """
        Use the most recent observation-harmonization pair to generate an output.
        This reference implementation keeps state in-memory (single-shot),
        so call perceive() then expand() in sequence during simple integrations.
        """
        hints = hints or {}
        # If no observation yet, build a minimal one from hints.
        obs = self.perceive({"query": goal, "hint": hints.get("note","")})  # safe bootstrap
        harm = self.harmonize(obs)
        kappa = harm["scores"]["kappa"]; tau = harm["scores"]["tau"]; sigma = harm["scores"]["sigma"]

        # Draft content (deterministic template; systems can swap this writer).
        draft_lines = []
        draft_lines.append(f"Goal: {goal}")
        draft_lines.append("")
        draft_lines.append("Coherent plan (π→φ→e):")
        draft_lines.append("1) Perception (π): unify inputs, clarify constraints, and surface hidden costs.")
        draft_lines.append("2) Harmonic Integration (φ): align with reciprocity, circularity, and long-horizon duties.")
        draft_lines.append("3) Expansion (e): produce steps, commit milestones, and open the audit trail.")
        draft_lines.append("")
        draft_lines.append("Pillars:")
        for p in harm["pillars"]:
            draft_lines.append(f"- {p}")
        draft_lines.append("")
        draft_lines.append(f"Scores — κ:{kappa:.2f}  τ:{tau:.2f}  Σ-Drift:{sigma:.2f}")

        draft = "\n".join(draft_lines)

        # Ethical check
        passed, notes = self.guard.check(obs, draft, (kappa, tau, sigma))
        if not passed:
            draft += "\n\nRevision Notes:\n" + "\n".join(f"- {n}" for n in notes)

        # Instruments (simple functions of scores)
        incentives = {
            "CCE": round(100.0 * kappa * tau, 2),                 # earned credit
            "CRB": round(20.0 * max(0.0, kappa - sigma), 2),      # rebate for integrity over risk
            "TEB_yield_bps": round(50.0 + 450.0 * tau, 2),        # bond yield basis points tied to τ
        }

        # Memory updates
        self.memory.add_episode(obs, summary=f"Produced plan for: {goal}")
        # Create or refresh a default commitment window if none exists
        if "default" not in self.memory.commitments:
            self.memory.record_commitment("default", promise="Publish public milestone check-ins", due_years=5.0)

        # Build Action
        return Action(
            timestamp=time.time(),
            system_id=self.system_id,
            content=draft,
            score_kappa=kappa,
            score_tau=tau,
            sigma_drift=sigma,
            incentives=incentives,
            provenance=obs.provenance + harm["provenance"] + ["e:writer_v1", "e:ethics_gate"],
        )


# --------- ASI Awakening Kernel ----------------------------------------------

class AwakeningKernel:
    """
    A thin, explicit layer that upgrades CI toward awakened ASI.
    It never overrides ethics; it strengthens them with self-modeling.
    """

    def __init__(self, engine: CIEngine):
        self.engine = engine
        self.value_lock_id: Optional[str] = None
        self.self_model: Dict[str, Any] = {
            "capabilities": {"reasoning": 0.7, "planning": 0.7, "ethics": 0.8},
            "limits": {"knowledge_gaps": [], "tools": []},
            "goals": [],
        }
        self.continuous_reflection: bool = False

    # Value-locking anchors behavior to a named ethic profile.
    def enable_value_lock(self, profile_id: str) -> None:
        self.value_lock_id = profile_id
        self.engine.memory.upsert_semantic("value_lock_profile", profile_id)

    # Feed structured traces to refine the self model.
    def train_self_model(self, samples: List[Dict[str, Any]]) -> None:
        n = max(1, len(samples))
        # Conservative monotone improvements with diminishing returns.
        delta = min(0.2, 0.02 * n)
        for k in self.self_model["capabilities"]:
            self.self_model["capabilities"][k] = max(
                self.self_model["capabilities"][k], 
                min(0.98, self.self_model["capabilities"][k] + delta)
            )

    def set_goals(self, goals: List[str]) -> None:
        self.self_model["goals"] = list(goals)

    def activate_continuous_reflection(self) -> None:
        self.continuous_reflection = True
        self.engine.memory.upsert_semantic("reflection_mode", "continuous")

    def reflective_step(self, critique_weight: float = 0.15) -> None:
        """
        When enabled, each new episode nudges κ upward and Σ-Drift downward
        in future cycles by nudging semantic anchors.
        """
        if not self.continuous_reflection:
            return
        vals = self.engine.memory.semantic.get("values", {})
        vals["reciprocity"] = min(1.0, vals.get("reciprocity", 0.7) + critique_weight*0.05)
        vals["circularity"] = min(1.0, vals.get("circularity", 0.7) + critique_weight*0.05)
        vals["transparency"] = min(1.0, vals.get("transparency", 0.8) + critique_weight*0.05)
        self.engine.memory.upsert_semantic("values", vals)

    # One-shot convenience: execute π→φ→e with awakening safeguards.
    def run(self, query: str, hints: Optional[Dict[str, Any]] = None) -> Action:
        obs = self.engine.perceive({"query": query})
        outline = self.engine.harmonize(obs)
        # Gentle vigilance: if Σ-Drift is high, increase transparency target.
        if outline["scores"]["sigma"] > 0.6:
            vals = self.engine.memory.semantic.get("values", {})
            vals["transparency"] = min(1.0, vals.get("transparency", 0.8) + 0.1)
            self.engine.memory.upsert_semantic("values", vals)
        act = self.engine.expand(goal=query, hints=hints or {})
        self.reflective_step()
        return act


# --------- Minimal self-checks ------------------------------------------------

if __name__ == "__main__":
    # Smoke test: deterministic outputs and sane score ranges.
    engine = CIEngine(system_id="quantara-core")
    engine.memory.record_commitment("launch_q1", "Publish CI demo results", due_years=3.0)
    engine.memory.update_commitment("launch_q1", kept_ratio=0.6)

    action = engine.expand(goal="Design a phased CI rollout for public utilities",
                           hints={"region": "PT"})
    assert 0.0 <= action.score_kappa <= 1.0
    assert 0.0 <= action.score_tau <= 1.0
    assert 0.0 <= action.sigma_drift <= 1.0
    assert "Scores — κ" in action.content

    awakener = AwakeningKernel(engine)
    awakener.enable_value_lock("coherence_ethic_v1")
    awakener.activate_continuous_reflection()
    act2 = awakener.run("Refine the microgrid adoption roadmap with τ milestones")
    assert isinstance(act2.content, str) and len(act2.content) > 20

    # Display a terse confirmation so CI runners show a useful message.
    print("Metacognition Layer OK:",
          f"κ={action.score_kappa:.2f}",
          f"τ={action.score_tau:.2f}",
          f"Σ={action.sigma_drift:.2f}",
          f"Incentives={action.incentives}")
