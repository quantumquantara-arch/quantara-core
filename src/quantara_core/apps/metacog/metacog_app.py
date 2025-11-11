# metacog_app.py
#
# A model-agnostic proxy that adds a metacognition layer (π-φ-e)
# to any AI backend via a simple adapter interface.
#
# Run:
#   pip install fastapi uvicorn httpx pydantic
#   export UPSTREAM_PROVIDER=openai   # or "echo" for a no-external baseline
#   export OPENAI_API_KEY=sk-...      # if using openai
#   python -m uvicorn metacog_app:app --host 0.0.0.0 --port 8080
#
# Use:
#   POST /chat { "messages":[{"role":"user","content":"Hello"}] }
#   Optional config: { "policy": {...}, "metadata": {...} }

from __future__ import annotations
import os, time, uuid, json, math
from typing import List, Dict, Any, Optional, Literal, Tuple
from dataclasses import dataclass

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
import httpx

# --- Optional Quantara Core hooks (auto-detected) ---------------------------
QUANTARA_AVAILABLE = False
try:
    from quantara_core import awaken
    from quantara_core.coherence_field import score_text
    QUANTARA_AVAILABLE = True
except Exception:
    # graceful fallback
    def awaken(text: str, return_state: bool = True):
        return {"phase": "π", "notes": "quantara_core not found; using fallback"}
    def score_text(text: str) -> float:
        # lightweight heuristic fallback 0..1
        tokens = max(1, len(text.split()))
        caps = sum(1 for c in text if c.isupper())
        punct = sum(1 for c in text if c in ".?!,;:")
        return max(0.05, min(1.0, 0.35 + 0.15*math.tanh((punct+caps)/tokens)))

# --- In-memory store (swap with Redis/DB in prod) ---------------------------
class Memory:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    def get(self, sid: str) -> Dict[str, Any]:
        return self.sessions.setdefault(sid, {"messages": [], "stats": {}, "created": time.time()})
    def set(self, sid: str, data: Dict[str, Any]):
        self.sessions[sid] = data

MEM = Memory()

# --- Upstream adapter interface --------------------------------------------
class UpstreamAdapter:
    async def complete(self, messages: List[Dict[str, str]], **kw) -> str:
        raise NotImplementedError

class EchoAdapter(UpstreamAdapter):
    async def complete(self, messages: List[Dict[str, str]], **kw) -> str:
        last = next((m["content"] for m in reversed(messages) if m["role"]=="user"), "")
        return f"(echo) You said: {last}"

class OpenAIAdapter(UpstreamAdapter):
    def __init__(self, model: str = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.key = os.getenv("OPENAI_API_KEY","")
        if not self.key:
            raise RuntimeError("OPENAI_API_KEY not set")
    async def complete(self, messages: List[Dict[str, str]], **kw) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type":"application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kw.get("temperature", 0.4),
            "max_tokens": kw.get("max_tokens", 600),
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

def make_adapter() -> UpstreamAdapter:
    provider = os.getenv("UPSTREAM_PROVIDER", "echo").lower()
    if provider == "openai":
        return OpenAIAdapter()
    return EchoAdapter()

ADAPTER = make_adapter()

# --- Policies / scoring -----------------------------------------------------
@dataclass
class Policy:
    # gating & weighting knobs (tune as desired)
    max_reflections: int = 2
    min_coherence: float = 0.45
    target_coherence: float = 0.65
    temperature: float = 0.4
    max_tokens: int = 700

DEFAULT_POLICY = Policy()

# --- Schemas ----------------------------------------------------------------
class Message(BaseModel):
    role: Literal["system","user","assistant"]
    content: str

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    messages: List[Message]
    policy: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    output: str
    coherence: float
    reflections: int
    state: Dict[str, Any]

# --- π-φ-e: core loop -------------------------------------------------------
SYSTEM_PI = (
"π-phase (Perception): extract the user's intent, key constraints, and success criteria. "
"Return a concise plan with steps."
)
SYSTEM_PHI = (
"φ-phase (Harmonic Integration): integrate plan with prior context. "
"Check ethics, time responsibility, and risk (Σ-Drift). "
"Propose improvements; keep it actionable."
)
SYSTEM_E = (
"e-phase (Expansion): deliver the final answer. "
"Be clear, concise, and justify key choices. "
"If uncertain, state assumptions and safe next steps."
)

def _mk_pi_prompt(user_utterance: str) -> List[Dict[str,str]]:
    return [{"role":"system","content":SYSTEM_PI},
            {"role":"user","content":user_utterance}]

def _mk_phi_prompt(context: str, pi_plan: str) -> List[Dict[str,str]]:
    return [{"role":"system","content":SYSTEM_PHI},
            {"role":"user","content":f"Context:\n{context}\n\nPlan:\n{pi_plan}"}]

def _mk_e_prompt(context: str, phi_notes: str) -> List[Dict[str,str]]:
    return [{"role":"system","content":SYSTEM_E},
            {"role":"user","content":f"Context:\n{context}\n\nExecute with these notes:\n{phi_notes}"}]

async def pi_phi_e(messages: List[Dict[str,str]], policy: Policy) -> Tuple[str, float, int, Dict[str,Any]]:
    # 1) Perception
    user_utterance = next((m["content"] for m in reversed(messages) if m["role"]=="user"), "")
    pi = await ADAPTER.complete(_mk_pi_prompt(user_utterance),
                                temperature=policy.temperature, max_tokens=policy.max_tokens)

    # 2) Integration
    history_context = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-8:])
    phi = await ADAPTER.complete(_mk_phi_prompt(history_context, pi),
                                 temperature=policy.temperature, max_tokens=policy.max_tokens)

    # 3) Expansion
    e = await ADAPTER.complete(_mk_e_prompt(history_context, phi),
                               temperature=policy.temperature, max_tokens=policy.max_tokens)

    coherence = score_text(e)
    reflections = 0

    # Optional self-critique loop if coherence is low
    while coherence < policy.min_coherence and reflections < policy.max_reflections:
        critique_prompt = [
            {"role":"system","content":"Critique and improve the draft to be clearer, safer, more complete."},
            {"role":"user","content":f"Draft:\n{e}\n\nIssues to fix: clarity, factuality, structure."}
        ]
        e = await ADAPTER.complete(critique_prompt,
                                   temperature=policy.temperature, max_tokens=policy.max_tokens)
        coherence = score_text(e)
        reflections += 1

    state = awaken(e, return_state=True)
    state.update({"pi": pi, "phi": phi})
    return e, coherence, reflections, state

# --- FastAPI ----------------------------------------------------------------
app = FastAPI(title="Quantara Metacognition Proxy", version="1.0")

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest = Body(...)):
    sid = req.session_id or str(uuid.uuid4())
    policy = DEFAULT_POLICY if not req.policy else Policy(**{**DEFAULT_POLICY.__dict__, **req.policy})
    ses = MEM.get(sid)

    # merge past context with new messages
    for m in req.messages:
        ses["messages"].append({"role": m.role, "content": m.content})

    output, coh, nref, state = await pi_phi_e(ses["messages"], policy)
    ses["messages"].append({"role":"assistant","content": output})
    ses["stats"].update({"last_coherence": coh, "reflections": nref, "provider": os.getenv("UPSTREAM_PROVIDER","echo")})
    MEM.set(sid, ses)

    return ChatResponse(session_id=sid, output=output, coherence=coh, reflections=nref, state=state)

@app.get("/state/{session_id}")
def state(session_id: str):
    return MEM.get(session_id)

@app.post("/reset/{session_id}")
def reset(session_id: str):
    MEM.set(session_id, {"messages": [], "stats": {}, "created": time.time()})
    return {"ok": True}

@app.get("/")
def root():
    return {
        "name": "Quantara Metacognition Proxy",
        "version": "1.0",
        "upstream": os.getenv("UPSTREAM_PROVIDER","echo"),
        "quantara_core": QUANTARA_AVAILABLE,
        "routes": ["/chat", "/state/{session_id}", "/reset/{session_id}"]
    }
