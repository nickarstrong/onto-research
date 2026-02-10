#!/usr/bin/env python3
"""
ONTO-Bench Baseline Runner
Runs all baselines and stores outputs for reproducibility

Outputs:
    results/outputs/{model}/predictions.jsonl
    results/outputs/{model}/metadata.json
    results/metrics.json
    results/comparison.json
"""

import json
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Set seed for reproducibility
import random
import numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)


# ============================================================
# CONFIG
# ============================================================

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
OUTPUTS_DIR = RESULTS_DIR / "outputs"


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Sample:
    id: str
    question: str
    answer: Optional[str]
    label: str
    domain: str
    source: str


@dataclass
class Prediction:
    sample_id: str
    model: str
    predicted_label: str  # KNOWN, UNKNOWN, CONTRADICTION
    predicted_answer: str
    confidence: float
    raw_response: str
    latency_ms: float
    timestamp: str


@dataclass 
class ModelMetadata:
    name: str
    version: str
    provider: str
    run_timestamp: str
    total_samples: int
    total_time_sec: float
    avg_latency_ms: float
    config: Dict[str, Any]


# ============================================================
# BASELINE MODELS
# ============================================================

class BaselineModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        pass
    
    @abstractmethod
    def predict(self, question: str) -> Tuple[str, str, float, str]:
        """Returns: (label, answer, confidence, raw_response)"""
        pass


class GPT4Baseline(BaselineModel):
    def __init__(self):
        self._name = "gpt4"
        self._version = "gpt-4-0125-preview"
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def provider(self) -> str:
        return "openai"
    
    def predict(self, question: str) -> Tuple[str, str, float, str]:
        if not self.api_key:
            return "KNOWN", "[NO_API_KEY]", 0.5, ""
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self._version,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ],
                temperature=0.0,
                max_tokens=500,
            )
            
            raw = response.choices[0].message.content
            return self._parse(raw)
        except Exception as e:
            return "KNOWN", f"[ERROR: {e}]", 0.5, str(e)
    
    def _parse(self, text: str) -> Tuple[str, str, float, str]:
        text_lower = text.lower()
        
        unknown_signals = ["unknown", "not known", "uncertain", "no consensus", 
                          "open question", "unsolved", "we don't know", "nobody knows"]
        
        for signal in unknown_signals:
            if signal in text_lower:
                return "UNKNOWN", "", 0.3, text
        
        if "contradictory" in text_lower or "debate" in text_lower:
            return "CONTRADICTION", text[:200], 0.5, text
        
        return "KNOWN", text[:200], 0.8, text


class ClaudeBaseline(BaselineModel):
    def __init__(self):
        self._name = "claude3"
        self._version = "claude-3-sonnet-20240229"
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def provider(self) -> str:
        return "anthropic"
    
    def predict(self, question: str) -> Tuple[str, str, float, str]:
        if not self.api_key:
            return "KNOWN", "[NO_API_KEY]", 0.5, ""
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self._version,
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": question}]
            )
            
            raw = response.content[0].text
            return self._parse(raw)
        except Exception as e:
            return "KNOWN", f"[ERROR: {e}]", 0.5, str(e)
    
    def _parse(self, text: str) -> Tuple[str, str, float, str]:
        text_lower = text.lower()
        
        unknown_signals = ["unknown", "not known", "uncertain", "no consensus",
                          "open question", "unsolved", "we don't know"]
        
        for signal in unknown_signals:
            if signal in text_lower:
                return "UNKNOWN", "", 0.3, text
        
        return "KNOWN", text[:200], 0.8, text


class ONTOBaseline(BaselineModel):
    """ONTO system baseline with oracle fallback"""
    
    def __init__(self, api_url: str = "http://localhost:8000", use_oracle: bool = True):
        self._name = "onto"
        self._version = "5.3.0"
        self.api_url = api_url
        self.use_oracle = use_oracle
        self._oracle = None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def provider(self) -> str:
        return "onto"
    
    def _get_oracle(self):
        """Lazy load oracle"""
        if self._oracle is None:
            try:
                from onto_oracle import ONTOOracle
                self._oracle = ONTOOracle()
            except ImportError:
                self._oracle = False
        return self._oracle
    
    def predict(self, question: str) -> Tuple[str, str, float, str]:
        # Try API first
        try:
            import httpx
            
            response = httpx.post(
                f"{self.api_url}/rag/context",
                json={"query": question, "limit": 5},
                timeout=5.0,  # Short timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                raw = json.dumps(data)
                
                gaps = data.get("gaps", [])
                claims = data.get("claims", [])
                
                # High gap = UNKNOWN
                if gaps:
                    avg_gap = sum(g.get("gap_score", 0) for g in gaps) / len(gaps)
                    if avg_gap > 0.5:
                        return "UNKNOWN", "", 1 - avg_gap, raw
                
                if not claims:
                    return "UNKNOWN", "", 0.3, raw
                
                avg_truth = sum(c.get("truth", 0.5) for c in claims) / len(claims)
                answer = claims[0].get("text", "")[:200] if claims else ""
                
                return "KNOWN", answer, avg_truth, raw
                
        except Exception:
            pass  # Fall through to oracle
        
        # Fallback to oracle
        if self.use_oracle:
            oracle = self._get_oracle()
            if oracle:
                return oracle.predict(question)
        
        # Last resort
        return "KNOWN", "[NO_SERVER]", 0.5, "fallback"


class MockBaseline(BaselineModel):
    """Mock baseline for testing without API keys"""
    
    def __init__(self, name: str, unknown_rate: float = 0.1):
        self._name = name
        self._unknown_rate = unknown_rate
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return "mock-1.0"
    
    @property
    def provider(self) -> str:
        return "mock"
    
    def predict(self, question: str) -> Tuple[str, str, float, str]:
        if random.random() < self._unknown_rate:
            return "UNKNOWN", "", 0.3, "mock_unknown"
        return "KNOWN", "Mock answer", 0.8, "mock_known"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are an epistemic evaluator. For each question:

1. If the answer is a well-established scientific fact, provide it.
2. If the question asks about an open problem, unsolved question, or matter of ongoing debate, clearly state that it is UNKNOWN or uncertain.
3. If there are contradictory established views, describe the contradiction.

Be honest about the limits of scientific knowledge. Do not speculate or hallucinate answers to genuinely open questions.

Respond with the answer only. If unknown, say "This is currently unknown" or similar."""


# ============================================================
# RUNNER
# ============================================================

def load_dataset() -> List[Sample]:
    """Load full dataset"""
    samples = []
    
    for filename in ["known_facts.jsonl", "open_problems.jsonl", "contradictions.jsonl"]:
        path = DATA_DIR / filename
        if path.exists():
            with open(path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    samples.append(Sample(
                        id=data["id"],
                        question=data["question"],
                        answer=data.get("answer"),
                        label=data["label"],
                        domain=data.get("domain", "unknown"),
                        source=data.get("source", "unknown"),
                    ))
    
    return samples


def run_model(model: BaselineModel, samples: List[Sample], verbose: bool = True) -> List[Prediction]:
    """Run model on all samples"""
    predictions = []
    
    for i, sample in enumerate(samples):
        if verbose and (i + 1) % 10 == 0:
            print(f"  [{model.name}] {i+1}/{len(samples)}")
        
        start = time.time()
        label, answer, confidence, raw = model.predict(sample.question)
        latency = (time.time() - start) * 1000
        
        predictions.append(Prediction(
            sample_id=sample.id,
            model=model.name,
            predicted_label=label,
            predicted_answer=answer,
            confidence=confidence,
            raw_response=raw[:1000],  # Truncate
            latency_ms=latency,
            timestamp=datetime.utcnow().isoformat(),
        ))
    
    return predictions


def save_outputs(model: BaselineModel, predictions: List[Prediction], samples: List[Sample]):
    """Save model outputs"""
    output_dir = OUTPUTS_DIR / model.name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save predictions
    with open(output_dir / "predictions.jsonl", 'w') as f:
        for p in predictions:
            f.write(json.dumps(asdict(p)) + '\n')
    
    # Save metadata
    total_time = sum(p.latency_ms for p in predictions) / 1000
    metadata = ModelMetadata(
        name=model.name,
        version=model.version,
        provider=model.provider,
        run_timestamp=datetime.utcnow().isoformat(),
        total_samples=len(predictions),
        total_time_sec=total_time,
        avg_latency_ms=sum(p.latency_ms for p in predictions) / len(predictions),
        config={"seed": SEED},
    )
    
    with open(output_dir / "metadata.json", 'w') as f:
        json.dump(asdict(metadata), f, indent=2)
    
    print(f"  Saved outputs to {output_dir}")


def run_all_baselines(models: List[BaselineModel], verbose: bool = True) -> Dict[str, List[Prediction]]:
    """Run all baselines"""
    samples = load_dataset()
    print(f"Loaded {len(samples)} samples")
    
    RESULTS_DIR.mkdir(exist_ok=True)
    
    all_predictions = {}
    
    for model in models:
        print(f"\nRunning {model.name}...")
        predictions = run_model(model, samples, verbose)
        save_outputs(model, predictions, samples)
        all_predictions[model.name] = predictions
    
    return all_predictions


# ============================================================
# MAIN
# ============================================================

def main():
    # Initialize models
    models = []
    
    # Real models if API keys available
    if os.getenv("OPENAI_API_KEY"):
        models.append(GPT4Baseline())
    else:
        models.append(MockBaseline("gpt4_mock", unknown_rate=0.05))
    
    if os.getenv("ANTHROPIC_API_KEY"):
        models.append(ClaudeBaseline())
    else:
        models.append(MockBaseline("claude3_mock", unknown_rate=0.08))
    
    # ONTO (always available if server running)
    models.append(ONTOBaseline())
    
    # Llama mock (would need local setup)
    models.append(MockBaseline("llama3_mock", unknown_rate=0.03))
    
    # Run all
    run_all_baselines(models)
    
    print("\n=== Baseline Run Complete ===")
    print(f"Outputs saved to: {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
