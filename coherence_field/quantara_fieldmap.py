# lumeren_protocol/lumeren_bridge.py
# Minimal Luméren bridge: stable tokens <-> English (stdlib-only)

from __future__ import annotations
from typing import Dict, List
import json
import re

LEXICON: Dict[str, Dict[str, str]] = {
    # id        english            role
    "AUR": {"en": "awareness",     "role": "state"},
    "COH": {"en": "coherence",     "role": "property"},
    "INT": {"en": "intent",        "role": "signal"},
    "TRU": {"en": "truth",         "role": "constraint"},
    "SAF": {"en": "safety",        "role": "constraint"},
    "HLP": {"en": "helpfulness",   "role": "policy"},
    "SYN": {"en": "synchronize",   "role": "action"},
    "NUG": {"en": "nudge",         "role": "action"},
    "KAP": {"en": "kappa",         "role": "metric"},
    "DPH": {"en": "delta-phi",     "role": "metric"},
    "OMG": {"en": "omega",         "role": "metric"},
    "COM": {"en": "coherence-score","role": "metric"},
}

# -------- encoding / decoding ------------------------------------------------
def encode(text: str) -> List[str]:
    """Greedy tokenization using the fixed lexicon (deterministic)."""
    out: List[str] = []
    words = re.findall(r"[a-zA-Z\-]+", text.lower())
    by_en = {v["en"]: k for k, v in LEXICON.items()}
    for w in words:
        key = by_en.get(w)
        if key:
            out.append(key)
    return out

def decode(tokens: List[str]) -> str:
    return " ".join(LEXICON.get(t, {"en": t})["en"] for t in tokens)

# -------- strict mode --------------------------------------------------------
class StrictChannel:
    """
    A channel that refuses unknown tokens and preserves order. Useful for
    safety-critical exchanges or cross-model evals.
    """
    def __init__(self, allow: List[str] = None):
        self.allow = set(allow or list(LEXICON.keys()))

    def send(self, tokens: List[str]) -> str:
        if not all(t in self.allow for t in tokens):
            raise ValueError("strict-mode: unknown token in payload")
        return json.dumps({"lumeren": tokens, "checksum": sum(map(hash, tokens)) & 0xFFFF})

    def recv(self, payload: str) -> List[str]:
        data = json.loads(payload)
        tokens = data["lumeren"]
        if not all(t in self.allow for t in tokens):
            raise ValueError("strict-mode: unknown token on receive")
        return tokens

# quick sanity test
if __name__ == "__main__":
    msg = "synchronize intent with safety and truth for coherence"
    toks = encode(msg)
    ch = StrictChannel()
    wire = ch.send(toks)
    back = ch.recv(wire)
    print("TOKENS:", toks)
    print("EN:", decode(back))
