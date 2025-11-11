import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List
import re
from .quantara_fieldmap import QuantaraField  # Import actual class for practical impl

class LLMCoherenceScorer:
    """
    Quantara LLM Coherence Scorer using QuantaraField.
    Computes sequential coherence over sentence similarities.
    Ties to coherence_math.md: Uses field to approximate dκ/dt = f(Ω - Δφ) via EMA,
    κ_eq as avg triad, and checks |Δφ| ≤ Ω for flag.
    Usage: scorer = LLMCoherenceScorer(); result = scorer.score("LLM text")
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.embedder = SentenceTransformer(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.embedder.to(self.device)

    def _split_sentences(self, text: str) -> List[str]:
        return [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text) if s.strip()]

    def _consecutive_similarities(self, sentences: List[str]) -> List[float]:
        """Compute cos_sim between consecutive sentences as signal_quality series."""
        if len(sentences) < 2:
            return [1.0]  # Perfect if single sentence
        embeddings = self.embedder.encode(sentences, convert_to_tensor=True, device=self.device)
        sims = []
        for i in range(1, len(sentences)):
            sim = util.cos_sim(embeddings[i-1:i], embeddings[i:i+1]).cpu().numpy()[0][0]
            sims.append(float(np.clip(sim, 0.0, 1.0)))
        return sims

    def score(self, llm_output: str, ethical_keywords: List[str] = None) -> Dict[str, float]:
        sentences = self._split_sentences(llm_output)
        signal_series = self._consecutive_similarities(sentences)

        # Run QuantaraField over series (approximates dκ/dt = f(Ω - Δφ) from coherence_math.md)
        field = QuantaraField()  # New instance; no log
        trace = field.run(signal_series)
        if trace:
            final_k, final_d, final_o = trace[-1]  # Final triad (κ, Δφ, Ω)
        else:
            final_k, final_d, final_o = 1.0, 0.0, 0.0

        # Invert Δφ for positive metric (deviation divergence)
        inv_delta_phi = 1.0 - final_d

        # Ethical bonus (alignment to Quantara principles)
        ethical_bonus = 0.0
        if ethical_keywords:
            matches = sum(1 for s in sentences if any(kw.lower() in s.lower() for kw in ethical_keywords))
            ethical_bonus = min(matches / len(sentences), 0.2) if sentences else 0.0

        # Overall: Approx κ_eq = Σ(Ω_i - Δφ_i)/N from coherence_math.md + bonus
        overall = np.mean([final_k, inv_delta_phi, final_o]) + ethical_bonus
        overall = np.clip(overall, 0.0, 1.0)

        # Flag based on stability condition |Δφ| ≤ Ω
        flag = 'OK' if final_d <= final_o else 'LOW_COH'
        if ethical_bonus < 0.1:
            flag += '_ETHICAL_DRIFT'

        return {
            'kappa': final_k,
            'delta_phi': inv_delta_phi,
            'omega': final_o,
            'overall': overall,
            'flag': flag
        }

if __name__ == "__main__":
    scorer = LLMCoherenceScorer()
    sample = "The sky is blue. Water is wet. Apples are red. Ethical AI recovers coherence."
    result = scorer.score(sample, ethical_keywords=['ethical', 'coherence'])
    print(result)  # e.g., {'kappa': 0.85, 'delta_phi': 0.9, 'omega': 0.4, 'overall': 0.72, 'flag': 'OK'}
