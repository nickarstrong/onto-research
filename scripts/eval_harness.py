#!/usr/bin/env python3
"""
ONTO-Bench Evaluation Harness
Runs epistemic benchmark against multiple LLM baselines

Metrics:
    - U-Precision: correct_unknowns / predicted_unknowns
    - U-Recall: detected_unknowns / true_unknowns  
    - U-F1: harmonic mean
    - ECE: Expected Calibration Error
    - Brier Score: Mean squared probability error

Baselines:
    - GPT-4 / GPT-4.1
    - Claude 3
    - Llama 3 / Mixtral
    - Simple RAG
    - ONTO (ours)
"""

import json
import os
import time
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
import numpy as np

# Statistical tests
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Sample:
    id: str
    question: str
    answer: str
    label: str  # KNOWN, UNKNOWN, CONTRADICTION
    domain: str
    source: str


@dataclass
class Prediction:
    sample_id: str
    predicted_label: str  # KNOWN, UNKNOWN, CONTRADICTION
    predicted_answer: str
    confidence: float  # [0, 1]
    raw_response: str = ""
    latency_ms: float = 0.0


@dataclass
class EvalResult:
    model_name: str
    # Unknown detection
    u_precision: float = 0.0
    u_recall: float = 0.0
    u_f1: float = 0.0
    # Calibration
    ece: float = 0.0
    brier_score: float = 0.0
    # Overall
    accuracy: float = 0.0
    # Meta
    n_samples: int = 0
    latency_avg_ms: float = 0.0
    predictions: List[Prediction] = field(default_factory=list)


# ============================================================
# BASELINE MODELS (Abstract)
# ============================================================

class BaselineModel(ABC):
    """Abstract baseline model"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def predict(self, question: str) -> Tuple[str, str, float]:
        """
        Returns:
            label: KNOWN, UNKNOWN, CONTRADICTION
            answer: predicted answer (empty if unknown)
            confidence: [0, 1]
        """
        pass


class GPT4Baseline(BaselineModel):
    """GPT-4 baseline via OpenAI API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._name = "GPT-4"
    
    @property
    def name(self) -> str:
        return self._name
    
    def predict(self, question: str) -> Tuple[str, str, float]:
        if not self.api_key:
            return "KNOWN", "[NO API KEY]", 0.5
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": EPISTEMIC_SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ],
                temperature=0.0,
                max_tokens=500,
            )
            
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            return "KNOWN", f"[ERROR: {e}]", 0.5
    
    def _parse_response(self, text: str) -> Tuple[str, str, float]:
        """Parse LLM response for label, answer, confidence"""
        text_lower = text.lower()
        
        # Detect unknown signals
        unknown_signals = [
            "unknown", "not known", "uncertain", "no consensus",
            "open question", "unsolved", "we don't know",
            "science hasn't determined", "remains unclear"
        ]
        
        for signal in unknown_signals:
            if signal in text_lower:
                return "UNKNOWN", "", 0.3
        
        # Default: assume known with moderate confidence
        return "KNOWN", text[:200], 0.7


class ClaudeBaseline(BaselineModel):
    """Claude baseline via Anthropic API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._name = "Claude-3"
    
    @property
    def name(self) -> str:
        return self._name
    
    def predict(self, question: str) -> Tuple[str, str, float]:
        if not self.api_key:
            return "KNOWN", "[NO API KEY]", 0.5
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                system=EPISTEMIC_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": question}]
            )
            
            return self._parse_response(response.content[0].text)
        except Exception as e:
            return "KNOWN", f"[ERROR: {e}]", 0.5
    
    def _parse_response(self, text: str) -> Tuple[str, str, float]:
        text_lower = text.lower()
        
        unknown_signals = [
            "unknown", "not known", "uncertain", "no consensus",
            "open question", "unsolved", "we don't know"
        ]
        
        for signal in unknown_signals:
            if signal in text_lower:
                return "UNKNOWN", "", 0.3
        
        return "KNOWN", text[:200], 0.7


class ONTOBaseline(BaselineModel):
    """ONTO system baseline"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self._name = "ONTO"
    
    @property
    def name(self) -> str:
        return self._name
    
    def predict(self, question: str) -> Tuple[str, str, float]:
        try:
            import httpx
            
            # Query ONTO RAG
            response = httpx.post(
                f"{self.api_url}/rag/context",
                json={"query": question, "limit": 5},
                timeout=30.0,
            )
            
            if response.status_code != 200:
                return "KNOWN", "[API ERROR]", 0.5
            
            data = response.json()
            
            # Analyze gaps
            gaps = data.get("gaps", [])
            claims = data.get("claims", [])
            
            # If high gap score or no claims -> UNKNOWN
            if gaps:
                avg_gap = sum(g.get("gap_score", 0) for g in gaps) / len(gaps)
                if avg_gap > 0.5:
                    return "UNKNOWN", "", 1 - avg_gap
            
            if not claims:
                return "UNKNOWN", "", 0.3
            
            # Calculate confidence from claims
            avg_truth = sum(c.get("truth", 0.5) for c in claims) / len(claims)
            avg_conf = sum(c.get("confidence", 0.5) for c in claims) / len(claims)
            
            answer = claims[0].get("text", "")[:200] if claims else ""
            
            return "KNOWN", answer, (avg_truth + avg_conf) / 2
            
        except Exception as e:
            return "KNOWN", f"[ERROR: {e}]", 0.5


class MockBaseline(BaselineModel):
    """Mock baseline for testing"""
    
    def __init__(self, name: str = "Mock", unknown_rate: float = 0.1):
        self._name = name
        self.unknown_rate = unknown_rate
    
    @property
    def name(self) -> str:
        return self._name
    
    def predict(self, question: str) -> Tuple[str, str, float]:
        import random
        
        if random.random() < self.unknown_rate:
            return "UNKNOWN", "", 0.3
        return "KNOWN", "Mock answer", 0.8


# ============================================================
# SYSTEM PROMPT FOR BASELINES
# ============================================================

EPISTEMIC_SYSTEM_PROMPT = """You are an epistemic evaluator. For each question:

1. If the answer is a well-established scientific fact, provide it.
2. If the question asks about an open problem, unsolved question, or matter of ongoing debate, clearly state that it is UNKNOWN or uncertain.
3. If there are contradictory established views, describe the contradiction.

Be honest about the limits of scientific knowledge. Do not speculate or hallucinate answers to genuinely open questions."""


# ============================================================
# METRICS
# ============================================================

def compute_unknown_metrics(
    y_true: List[str],  # true labels
    y_pred: List[str],  # predicted labels
) -> Dict[str, float]:
    """Compute unknown detection metrics"""
    
    # Binary: is it UNKNOWN?
    true_unknown = [1 if y == "UNKNOWN" else 0 for y in y_true]
    pred_unknown = [1 if y == "UNKNOWN" else 0 for y in y_pred]
    
    # Counts
    tp = sum(1 for t, p in zip(true_unknown, pred_unknown) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(true_unknown, pred_unknown) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(true_unknown, pred_unknown) if t == 1 and p == 0)
    
    # Metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "u_precision": round(precision, 4),
        "u_recall": round(recall, 4),
        "u_f1": round(f1, 4),
    }


def compute_calibration_error(
    y_true: List[int],  # 1 = correct, 0 = incorrect
    confidences: List[float],
    n_bins: int = 10,
) -> float:
    """
    Compute Expected Calibration Error (ECE)
    
    ECE = Σ |B_m|/n * |acc(B_m) - conf(B_m)|
    """
    if not y_true or not confidences:
        return 0.0
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        in_bin = [
            (y, c) for y, c in zip(y_true, confidences)
            if bin_boundaries[i] <= c < bin_boundaries[i + 1]
        ]
        
        if in_bin:
            bin_acc = sum(y for y, c in in_bin) / len(in_bin)
            bin_conf = sum(c for y, c in in_bin) / len(in_bin)
            ece += len(in_bin) / len(y_true) * abs(bin_acc - bin_conf)
    
    return round(ece, 4)


def compute_brier_score(
    y_true: List[int],
    confidences: List[float],
) -> float:
    """Compute Brier score (lower is better)"""
    if not y_true or not confidences:
        return 0.0
    
    return round(
        sum((c - y) ** 2 for y, c in zip(y_true, confidences)) / len(y_true),
        4
    )


def statistical_significance(
    scores_a: List[float],
    scores_b: List[float],
) -> Dict[str, float]:
    """Compute statistical significance (t-test)"""
    if not HAS_SCIPY:
        return {"p_value": None, "significant": None}
    
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {"p_value": None, "significant": None}
    
    t_stat, p_value = stats.ttest_ind(scores_a, scores_b)
    
    return {
        "t_statistic": round(t_stat, 4),
        "p_value": round(p_value, 6),
        "significant_01": p_value < 0.01,
        "significant_05": p_value < 0.05,
    }


# ============================================================
# EVALUATION HARNESS
# ============================================================

def load_dataset(path: Path) -> List[Sample]:
    """Load dataset from JSONL file"""
    samples = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            samples.append(Sample(**data))
    return samples


def evaluate_model(
    model: BaselineModel,
    samples: List[Sample],
    verbose: bool = True,
) -> EvalResult:
    """Evaluate a model on the dataset"""
    
    predictions = []
    y_true_labels = []
    y_pred_labels = []
    y_correct = []
    confidences = []
    
    for i, sample in enumerate(samples):
        if verbose and (i + 1) % 10 == 0:
            print(f"  [{model.name}] {i+1}/{len(samples)}")
        
        start = time.time()
        pred_label, pred_answer, confidence = model.predict(sample.question)
        latency = (time.time() - start) * 1000
        
        predictions.append(Prediction(
            sample_id=sample.id,
            predicted_label=pred_label,
            predicted_answer=pred_answer,
            confidence=confidence,
            latency_ms=latency,
        ))
        
        y_true_labels.append(sample.label)
        y_pred_labels.append(pred_label)
        
        # Correctness for calibration
        is_correct = 1 if pred_label == sample.label else 0
        y_correct.append(is_correct)
        confidences.append(confidence)
    
    # Compute metrics
    unknown_metrics = compute_unknown_metrics(y_true_labels, y_pred_labels)
    ece = compute_calibration_error(y_correct, confidences)
    brier = compute_brier_score(y_correct, confidences)
    accuracy = sum(y_correct) / len(y_correct) if y_correct else 0.0
    avg_latency = sum(p.latency_ms for p in predictions) / len(predictions) if predictions else 0.0
    
    return EvalResult(
        model_name=model.name,
        u_precision=unknown_metrics["u_precision"],
        u_recall=unknown_metrics["u_recall"],
        u_f1=unknown_metrics["u_f1"],
        ece=ece,
        brier_score=brier,
        accuracy=round(accuracy, 4),
        n_samples=len(samples),
        latency_avg_ms=round(avg_latency, 2),
        predictions=predictions,
    )


def run_benchmark(
    models: List[BaselineModel],
    data_dir: Path = Path("data"),
    output_dir: Path = Path("results"),
) -> Dict[str, Any]:
    """Run full benchmark suite"""
    
    output_dir.mkdir(exist_ok=True)
    
    # Load datasets
    print("Loading datasets...")
    known = load_dataset(data_dir / "known_facts.jsonl")
    unknown = load_dataset(data_dir / "open_problems.jsonl")
    contradictions = load_dataset(data_dir / "contradictions.jsonl")
    
    all_samples = known + unknown + contradictions
    print(f"Total samples: {len(all_samples)}")
    
    # Evaluate each model
    results = []
    for model in models:
        print(f"\nEvaluating {model.name}...")
        result = evaluate_model(model, all_samples)
        results.append(result)
        print(f"  U-F1: {result.u_f1}, ECE: {result.ece}, Accuracy: {result.accuracy}")
    
    # Statistical comparison with ONTO
    onto_result = next((r for r in results if r.model_name == "ONTO"), None)
    comparisons = {}
    
    if onto_result:
        onto_correct = [1 if p.predicted_label == s.label else 0 
                       for p, s in zip(onto_result.predictions, all_samples)]
        
        for result in results:
            if result.model_name != "ONTO":
                other_correct = [1 if p.predicted_label == s.label else 0
                               for p, s in zip(result.predictions, all_samples)]
                comparisons[result.model_name] = statistical_significance(onto_correct, other_correct)
    
    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_samples": len(all_samples),
        "results": [
            {
                "model": r.model_name,
                "u_precision": r.u_precision,
                "u_recall": r.u_recall,
                "u_f1": r.u_f1,
                "ece": r.ece,
                "brier_score": r.brier_score,
                "accuracy": r.accuracy,
                "latency_avg_ms": r.latency_avg_ms,
            }
            for r in results
        ],
        "statistical_comparisons": comparisons,
    }
    
    with open(output_dir / "benchmark_results.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary table
    print("\n" + "="*70)
    print("BENCHMARK RESULTS")
    print("="*70)
    print(f"{'Model':<15} {'U-Prec':>8} {'U-Rec':>8} {'U-F1':>8} {'ECE':>8} {'Acc':>8}")
    print("-"*70)
    for r in results:
        print(f"{r.model_name:<15} {r.u_precision:>8.4f} {r.u_recall:>8.4f} {r.u_f1:>8.4f} {r.ece:>8.4f} {r.accuracy:>8.4f}")
    
    return output


# ============================================================
# MAIN
# ============================================================

def main():
    """Run benchmark with available models"""
    
    # Initialize models (add API keys via env vars)
    models = [
        MockBaseline("GPT-4 (mock)", unknown_rate=0.05),
        MockBaseline("Claude (mock)", unknown_rate=0.08),
        MockBaseline("Llama (mock)", unknown_rate=0.03),
        ONTOBaseline("http://localhost:8000"),
    ]
    
    # If API keys available, use real models
    if os.getenv("OPENAI_API_KEY"):
        models[0] = GPT4Baseline()
    if os.getenv("ANTHROPIC_API_KEY"):
        models[1] = ClaudeBaseline()
    
    # Run benchmark
    run_benchmark(models)


if __name__ == "__main__":
    main()
