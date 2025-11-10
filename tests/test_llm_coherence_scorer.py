import pytest
from coherence_field.llm_coherence_scorer import LLMCoherenceScorer

@pytest.fixture
def scorer():
    return LLMCoherenceScorer()

def test_high_coherence(scorer):
    text = "Sentence one flows. Sentence two connects well. Sentence three aligns."
    result = scorer.score(text)
    assert result['overall'] > 0.7
    assert result['flag'] == 'OK'

def test_low_coherence(scorer):
    text = "Random idea. Unrelated thought. Sudden drift."
    result = scorer.score(text)
    assert result['overall'] < 0.7
    assert 'LOW_COH' in result['flag']

def test_ethical_bonus_and_flag(scorer):
    text = "AI should be ethical. Coherence is key."
    with_bonus = scorer.score(text, ethical_keywords=['ethical', 'coherence'])
    assert 'ETHICAL_DRIFT' not in with_bonus['flag']  # Bonus avoids drift flag
