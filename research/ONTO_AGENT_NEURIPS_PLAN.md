# ONTO-Agent: Epistemic Discovery through Structured Reasoning

## NeurIPS Research Plan

### Target Venue
- **Primary**: NeurIPS 2026 Main Track
- **Backup**: ICML 2026, ICLR 2027
- **Workshop**: NeurIPS Datasets & Benchmarks Track

---

## 1. Research Statement

### Title Options

1. "ONTO-Agent: Scientific Discovery through Epistemic Gap Detection"
2. "Forcing Knowledge Boundaries: Autonomous Discovery with Ontological Structure"
3. "Beyond Hallucination: Agents that Know What They Don't Know"

### One-Sentence Contribution

> We present ONTO-Agent, the first autonomous research agent that explicitly reasons about knowledge boundaries, achieving [X]% improvement in hypothesis quality over baseline agents by leveraging ontological gap detection.

---

## 2. Problem Statement

### The Discovery Problem

Current AI agents can retrieve and synthesize information but cannot:
1. Identify genuine gaps in scientific knowledge
2. Distinguish speculation from established fact
3. Generate hypotheses that address real unknowns
4. Update beliefs appropriately on new evidence

### Why This Matters

- **Scientific Progress**: Automated discovery requires knowing what's unknown
- **AI Safety**: Agents that can't recognize limits are unreliable
- **Efficiency**: Research effort wasted on solved problems

### Gap in Literature

| Approach | Knowledge Rep | Gap Detection | Hypothesis Gen |
|----------|---------------|---------------|----------------|
| RAG Agents | Documents | ❌ | ❌ |
| ReAct | None | ❌ | ❌ |
| AutoGPT | Implicit | ❌ | ❌ |
| **ONTO-Agent** | **Ontology** | **✓** | **✓** |

---

## 3. Technical Approach

### 3.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ONTO-Agent                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Epistemic Kernel                     │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐         │   │
│  │  │  Claim    │ │   Gap     │ │  Forcing  │         │   │
│  │  │  Store    │ │  Detector │ │  Engine   │         │   │
│  │  └───────────┘ └───────────┘ └───────────┘         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌───────────────────────▼───────────────────────────┐     │
│  │               Agent Modules                        │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │     │
│  │  │ Reader  │ │Reasoner │ │Hypothe- │ │ Writer  │ │     │
│  │  │         │ │         │ │ sizer   │ │         │ │     │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │     │
│  └───────────────────────────────────────────────────┘     │
│                          │                                  │
│  ┌───────────────────────▼───────────────────────────┐     │
│  │               External Tools                       │     │
│  │  • Semantic Scholar API                           │     │
│  │  • arXiv Search                                   │     │
│  │  • Code Execution                                 │     │
│  │  • Web Search                                     │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Epistemic Kernel

**Claim Store**: Structured knowledge base with epistemic annotations

```python
@dataclass
class Claim:
    content: str
    status: Literal["ESTABLISHED", "CONTESTED", "UNKNOWN", "HYPOTHESIZED"]
    confidence: float
    source: Source
    dependencies: List[ClaimID]
    evidence: List[Evidence]
```

**Gap Detector**: Identifies epistemic gaps in the knowledge base

```python
class GapDetector:
    def detect(self, query: Query) -> List[Gap]:
        gaps = []
        
        # 1. Missing dependency gaps
        for claim in self.relevant_claims(query):
            for dep in claim.dependencies:
                if not self.store.has(dep):
                    gaps.append(MissingDependency(claim, dep))
        
        # 2. Contradiction gaps
        contradictions = self.store.find_contradictions(query)
        for c1, c2 in contradictions:
            gaps.append(UnresolvedContradiction(c1, c2))
        
        # 3. Coverage gaps
        expected = self.expected_coverage(query)
        actual = self.store.coverage(query)
        if actual < expected:
            gaps.append(CoverageGap(query, expected - actual))
        
        return gaps
```

**Forcing Engine**: Principled mechanism for knowledge extension

```python
class ForcingEngine:
    def force(self, hypothesis: Claim, evidence: Evidence) -> Result:
        # 1. Consistency check
        if not self.consistent(hypothesis):
            return Result.REJECTED("Inconsistent with established claims")
        
        # 2. Evidence threshold
        strength = self.evaluate_evidence(evidence)
        if strength < THRESHOLD:
            return Result.INSUFFICIENT("Evidence below threshold")
        
        # 3. Add with appropriate status
        if strength > HIGH_THRESHOLD:
            hypothesis.status = "ESTABLISHED"
        else:
            hypothesis.status = "HYPOTHESIZED"
        
        self.store.add(hypothesis)
        
        # 4. Propagate implications
        self.propagate(hypothesis)
        
        return Result.ACCEPTED(hypothesis)
```

### 3.3 Agent Modules

**Reader Agent**: Extracts structured claims from literature

```python
class ReaderAgent:
    def read(self, paper: Paper) -> List[Claim]:
        # 1. Parse paper structure
        sections = self.parse(paper)
        
        # 2. Extract claims
        raw_claims = self.llm.extract_claims(sections)
        
        # 3. Classify epistemic status
        for claim in raw_claims:
            claim.status = self.classify_status(claim, paper)
        
        # 4. Resolve dependencies
        for claim in raw_claims:
            claim.dependencies = self.resolve_deps(claim, self.store)
        
        return raw_claims
```

**Hypothesizer Agent**: Generates hypotheses from detected gaps

```python
class HypothesizerAgent:
    def hypothesize(self, gap: Gap) -> List[Hypothesis]:
        # 1. Gather context
        context = self.store.context_for(gap)
        
        # 2. Generate candidates
        candidates = self.llm.generate_hypotheses(
            gap=gap,
            context=context,
            n=5,
        )
        
        # 3. Filter by consistency
        consistent = [h for h in candidates if self.kernel.consistent(h)]
        
        # 4. Rank by plausibility
        ranked = self.rank_by_plausibility(consistent)
        
        return ranked
```

### 3.4 Discovery Loop

```python
def discovery_loop(agent: ONTOAgent, topic: str, max_iterations: int = 10):
    for i in range(max_iterations):
        # 1. Detect gaps
        gaps = agent.gap_detector.detect(topic)
        
        if not gaps:
            print("No gaps detected. Discovery complete.")
            break
        
        # 2. Prioritize
        gap = agent.prioritize(gaps)[0]
        
        # 3. Research
        papers = agent.search_literature(gap)
        for paper in papers:
            claims = agent.reader.read(paper)
            for claim in claims:
                agent.kernel.add(claim)
        
        # 4. Check if gap resolved
        if agent.gap_resolved(gap):
            continue
        
        # 5. Hypothesize
        hypotheses = agent.hypothesizer.hypothesize(gap)
        
        # 6. Evaluate hypotheses
        for h in hypotheses:
            evidence = agent.gather_evidence(h)
            result = agent.kernel.force(h, evidence)
            
            if result.accepted:
                print(f"New hypothesis accepted: {h}")
        
        # 7. Write findings
        if i % 5 == 0:
            agent.writer.summarize(topic)
```

---

## 4. Experiments

### 4.1 Evaluation Tasks

**Task 1: Gap Detection Accuracy**
- Input: Scientific papers with known gaps
- Output: Detected gaps
- Metric: Precision/Recall vs. human-annotated gaps

**Task 2: Hypothesis Quality**
- Input: Known historical gaps (pre-discovery)
- Output: Generated hypotheses
- Metric: Similarity to actual discoveries

**Task 3: Literature Review Quality**
- Input: Research topic
- Output: Generated survey
- Metric: Coverage, accuracy (human eval)

**Task 4: End-to-End Discovery**
- Input: Research area
- Output: Novel, validated hypotheses
- Metric: Expert evaluation, citation potential

### 4.2 Datasets

**GapBench** (New contribution)
- 500 annotated papers with explicit gaps
- 200 historical discoveries with pre/post states
- 100 expert-labeled hypothesis quality samples

**Existing Benchmarks**
- SciGen: Hypothesis generation
- QASPER: Scientific QA
- S2ORC: Literature corpus

### 4.3 Baselines

| Baseline | Description |
|----------|-------------|
| GPT-4 + CoT | Chain-of-thought prompting |
| ReAct | Reasoning + acting |
| Toolformer | Tool-augmented LM |
| AutoGPT | Autonomous agent |
| ScholarGPT | Academic-focused agent |

### 4.4 Ablations

1. **Without Gap Detector**: Replace with LLM uncertainty
2. **Without Forcing**: Accept all hypotheses
3. **Without Claim Store**: Use RAG only
4. **Without Reader**: Use raw paper text

### 4.5 Metrics

**Gap Detection**
- Gap Precision: Correct gaps / Detected gaps
- Gap Recall: Correct gaps / True gaps
- Gap F1: Harmonic mean

**Hypothesis Quality**
- Novelty: Not in training data
- Consistency: No contradictions with established facts
- Plausibility: Expert rating (1-5)
- Discovery Match: Similarity to actual discovery (for historical)

**End-to-End**
- Discovery Rate: Valid hypotheses per iteration
- Efficiency: Papers read per hypothesis
- Coverage: Fraction of gaps addressed

---

## 5. Expected Results

### Quantitative

| Metric | Baseline | ONTO-Agent | Δ |
|--------|----------|------------|---|
| Gap Precision | 0.30 | 0.75 | +150% |
| Gap Recall | 0.20 | 0.65 | +225% |
| Hypothesis Plausibility | 2.1 | 3.8 | +81% |
| Discovery Match | 0.15 | 0.45 | +200% |

### Qualitative

1. **Case Study 1**: ONTO-Agent identifies gap in protein folding → generates hypothesis → matches AlphaFold approach (retrospective)

2. **Case Study 2**: ONTO-Agent discovers unreported connection between two subfields → verified by domain expert

3. **Failure Analysis**: When gaps are poorly defined, hypothesis quality degrades

---

## 6. Contributions

1. **ONTO-Agent Architecture**: First agent with explicit epistemic kernel
2. **Forcing Mechanism**: Principled approach to knowledge extension
3. **GapBench Dataset**: Benchmark for gap detection and hypothesis quality
4. **Empirical Demonstration**: Significant improvement over baselines

---

## 7. Related Work

### Autonomous Agents
- AutoGPT, BabyAGI: No epistemic structure
- ReAct: Reasoning traces, no gap detection
- Toolformer: Tool use, no knowledge management

### Scientific Discovery
- AI Scientist (Sakana): Paper generation, no gap focus
- SciGen: Hypothesis generation without ontology
- Nobel Turing Challenge: Vision statement

### Knowledge Representation
- CYC: Massive ontology, not LLM-integrated
- Knowledge Graphs: Structure without epistemic status
- RAG: Retrieval without gap detection

---

## 8. Limitations & Future Work

### Limitations
1. Requires domain-specific ontology engineering
2. Hypothesis validation currently requires human expert
3. Computational cost of maintaining claim store

### Future Work
1. Automated ontology construction
2. Self-supervised hypothesis validation
3. Multi-agent collaborative discovery
4. Real-time literature monitoring

---

## 9. Timeline

```
Month 1-2: Core implementation
  - Epistemic kernel
  - Basic agents
  - Integration

Month 3-4: Dataset creation
  - GapBench curation
  - Annotation pipeline
  - Quality validation

Month 5-6: Experiments
  - Baseline runs
  - Ablation studies
  - Case studies

Month 7-8: Writing
  - Paper draft
  - Revisions
  - Camera-ready

Month 9: Submission
  - NeurIPS deadline: May 2026
```

---

## 10. Resources Needed

| Resource | Amount | Purpose |
|----------|--------|---------|
| Compute (GPU) | $20K | LLM inference, experiments |
| API costs | $10K | GPT-4, Claude for baselines |
| Annotation | $5K | Expert labeling for GapBench |
| **Total** | **$35K** | |

---

## 11. Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Baseline too strong | Medium | Focus on gap detection differential |
| Annotation quality | Medium | Multi-expert validation |
| Novelty questioned | Low | Emphasize epistemic kernel contribution |
| Reproducibility | Low | Full code release |

---

## 12. Paper Outline

```
Abstract (200 words)

1. Introduction (1.5 pages)
   - Discovery problem
   - Epistemic gap
   - Contributions

2. Related Work (1 page)
   - Agents
   - Discovery
   - Knowledge rep

3. Method (3 pages)
   - Architecture
   - Epistemic kernel
   - Agent modules
   - Discovery loop

4. Experiments (2 pages)
   - Tasks
   - Datasets
   - Baselines
   - Results

5. Analysis (1 page)
   - Ablations
   - Case studies
   - Limitations

6. Conclusion (0.5 pages)

References (1 page)
Appendix (4 pages)
```

---

## 13. Key Figures

1. **Architecture Diagram**: Full system overview
2. **Gap Detection Pipeline**: Input → Gaps → Hypotheses
3. **Results Table**: Main comparison
4. **Ablation Chart**: Component contributions
5. **Case Study**: Visual walkthrough of discovery

---

*ONTO-Agent NeurIPS Research Plan v1.0*
