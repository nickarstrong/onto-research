# ONTO-OS Technical Specification v1.0

## Epistemic Operating System for AGI

---

## 1. Executive Overview

ONTO-OS is a runtime substrate that provides epistemic infrastructure for artificial general intelligence. It transforms AI from systems that generate plausible text into systems that reason about knowledge with structural integrity.

**Core Innovation**: Epistemic status as primitive, not derived.

---

## 2. Design Principles

### 2.1 Epistemic First

Every piece of information has explicit epistemic status:
- What is this? (content)
- How sure are we? (confidence)
- Where did it come from? (provenance)
- What does it depend on? (dependencies)
- What conflicts with it? (contradictions)

### 2.2 Structure Over Behavior

Safety through architecture, not prompting:
- Can't hallucinate facts (only established claims output as facts)
- Must acknowledge uncertainty (unknown status triggers disclosure)
- Auditable by design (full provenance chain)

### 2.3 Principled Extension

New knowledge added through forcing:
- Consistency guaranteed
- Evidence required
- Implications propagated
- Rollback possible

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ONTO-OS v1.0                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     APPLICATION LAYER                         │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │ │
│  │  │   Agents    │ │  Assistants │ │   Tools     │             │ │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘             │ │
│  └─────────┼───────────────┼───────────────┼────────────────────┘ │
│            └───────────────┼───────────────┘                       │
│                            ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     RUNTIME LAYER                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │ │
│  │  │   Query     │ │  Inference  │ │   Output    │             │ │
│  │  │   Parser    │ │   Engine    │ │  Generator  │             │ │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘             │ │
│  └─────────┼───────────────┼───────────────┼────────────────────┘ │
│            └───────────────┼───────────────┘                       │
│                            ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    EPISTEMIC LAYER                            │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │ │
│  │  │   Claim   │ │   Trust   │ │    Gap    │ │  Forcing  │    │ │
│  │  │  Registry │ │   Graph   │ │  Detector │ │  Engine   │    │ │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘    │ │
│  └────────┼─────────────┼─────────────┼─────────────┼───────────┘ │
│           └─────────────┼─────────────┼─────────────┘             │
│                         ▼             ▼                            │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    ONTOLOGY LAYER                             │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │ │
│  │  │  Concept  │ │ Relation  │ │   Axiom   │ │  Schema   │    │ │
│  │  │   Graph   │ │   Index   │ │   Store   │ │  Manager  │    │ │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘    │ │
│  └────────┼─────────────┼─────────────┼─────────────┼───────────┘ │
│           └─────────────┼─────────────┼─────────────┘             │
│                         ▼             ▼                            │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     STORAGE LAYER                             │ │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │ │
│  │  │   Neo4j   │ │  Qdrant   │ │ PostgreSQL│ │   Redis   │    │ │
│  │  │  (Graph)  │ │ (Vector)  │ │  (ACID)   │ │  (Cache)  │    │ │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Core Data Structures

### 4.1 Claim

The fundamental unit of knowledge:

```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from datetime import datetime
import hashlib

class EpistemicStatus(Enum):
    ESTABLISHED = "established"  # Consensus, high confidence
    CONTESTED = "contested"      # Multiple valid positions
    UNKNOWN = "unknown"          # Genuinely open question
    HYPOTHESIZED = "hypothesized"  # Proposed, not verified
    REFUTED = "refuted"          # Disproven
    DEPRECATED = "deprecated"    # Superseded

@dataclass
class Claim:
    # Identity
    id: str
    content: str                    # Natural language
    formal: Optional[str] = None    # Formal logic representation
    
    # Epistemic properties
    status: EpistemicStatus = EpistemicStatus.UNKNOWN
    confidence: float = 0.0         # 0.0 - 1.0
    
    # Provenance
    source_id: str = ""
    source_type: str = ""           # paper, textbook, inference, user
    extraction_method: str = ""      # manual, llm, rule-based
    
    # Relations
    dependencies: List[str] = None  # Claims this depends on
    supports: List[str] = None      # Claims this supports
    contradicts: List[str] = None   # Claims this conflicts with
    
    # Metadata
    domain: str = ""
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    version: int = 1
    
    def __post_init__(self):
        if self.id is None:
            self.id = self._generate_id()
        if self.dependencies is None:
            self.dependencies = []
        if self.supports is None:
            self.supports = []
        if self.contradicts is None:
            self.contradicts = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def _generate_id(self) -> str:
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:12]
        return f"claim_{content_hash}"
    
    @property
    def is_actionable(self) -> bool:
        """Can this claim be used for inference?"""
        return self.status in [
            EpistemicStatus.ESTABLISHED,
            EpistemicStatus.HYPOTHESIZED
        ]
    
    @property
    def requires_disclosure(self) -> bool:
        """Should uncertainty be disclosed when using this?"""
        return self.status in [
            EpistemicStatus.CONTESTED,
            EpistemicStatus.UNKNOWN,
            EpistemicStatus.HYPOTHESIZED
        ]
```

### 4.2 Source

Provenance tracking:

```python
@dataclass
class Source:
    id: str
    type: str  # paper, textbook, database, web, model, user
    
    # Identity
    title: Optional[str] = None
    authors: List[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    
    # Trust
    trust_score: float = 0.5        # 0.0 - 1.0
    peer_reviewed: bool = False
    citation_count: int = 0
    retraction_count: int = 0
    
    # Domain expertise
    domain_scores: Dict[str, float] = None  # domain -> expertise
    
    # Metadata
    publication_date: Optional[datetime] = None
    accessed_at: datetime = None
    
    def domain_trust(self, domain: str) -> float:
        """Trust score for specific domain"""
        base = self.trust_score
        domain_factor = self.domain_scores.get(domain, 0.5) if self.domain_scores else 0.5
        return base * domain_factor
```

### 4.3 Gap

Epistemic gap representation:

```python
class GapType(Enum):
    MISSING_DEPENDENCY = "missing_dependency"
    UNRESOLVED_CONTRADICTION = "contradiction"
    COVERAGE_GAP = "coverage"
    STALE_CLAIM = "stale"
    ORPHAN_CONCEPT = "orphan"

@dataclass
class Gap:
    id: str
    type: GapType
    description: str
    
    # Context
    related_claims: List[str] = None
    related_concepts: List[str] = None
    
    # Severity
    priority: float = 0.5           # 0.0 - 1.0
    impact_scope: int = 0           # Number of affected claims
    
    # Resolution
    resolution_hints: List[str] = None
    resolved: bool = False
    resolved_by: Optional[str] = None  # Claim ID that resolved this
```

---

## 5. Epistemic Layer APIs

### 5.1 Claim Registry

```python
class ClaimRegistry:
    """Central registry for all claims"""
    
    def add(self, claim: Claim) -> str:
        """Add claim to registry"""
        pass
    
    def get(self, claim_id: str) -> Optional[Claim]:
        """Retrieve claim by ID"""
        pass
    
    def query(self, 
              content: str = None,
              status: EpistemicStatus = None,
              domain: str = None,
              min_confidence: float = None) -> List[Claim]:
        """Query claims with filters"""
        pass
    
    def update_status(self, claim_id: str, 
                      new_status: EpistemicStatus,
                      reason: str) -> bool:
        """Update claim's epistemic status"""
        pass
    
    def find_contradictions(self, claim: Claim) -> List[Tuple[Claim, Claim]]:
        """Find claims that contradict given claim"""
        pass
    
    def get_dependency_chain(self, claim_id: str) -> List[Claim]:
        """Get full dependency chain for claim"""
        pass
```

### 5.2 Gap Detector

```python
class GapDetector:
    """Identifies epistemic gaps in knowledge base"""
    
    def detect_all(self) -> List[Gap]:
        """Detect all gaps in current knowledge base"""
        gaps = []
        gaps.extend(self._detect_missing_dependencies())
        gaps.extend(self._detect_contradictions())
        gaps.extend(self._detect_coverage_gaps())
        gaps.extend(self._detect_stale_claims())
        return gaps
    
    def detect_for_query(self, query: str) -> List[Gap]:
        """Detect gaps relevant to specific query"""
        pass
    
    def _detect_missing_dependencies(self) -> List[Gap]:
        """Find claims with unresolved dependencies"""
        pass
    
    def _detect_contradictions(self) -> List[Gap]:
        """Find unresolved contradictions"""
        pass
    
    def _detect_coverage_gaps(self) -> List[Gap]:
        """Find areas with insufficient coverage"""
        pass
    
    def _detect_stale_claims(self) -> List[Gap]:
        """Find claims that need updating"""
        pass
```

### 5.3 Trust Graph

```python
class TrustGraph:
    """Manages source trust relationships"""
    
    def add_source(self, source: Source) -> str:
        """Register new source"""
        pass
    
    def update_trust(self, source_id: str, 
                     event: str,  # "citation", "retraction", "validation"
                     delta: float) -> float:
        """Update trust score based on event"""
        pass
    
    def propagate_trust(self, claim: Claim) -> float:
        """Compute claim confidence from source trust"""
        source = self.get_source(claim.source_id)
        base_trust = source.domain_trust(claim.domain)
        
        # Adjust for extraction method
        method_factor = {
            "manual": 1.0,
            "rule-based": 0.9,
            "llm": 0.7,
        }.get(claim.extraction_method, 0.5)
        
        # Adjust for corroboration
        corroboration = self._count_corroborating_sources(claim)
        corroboration_factor = min(1.0, 0.5 + 0.1 * corroboration)
        
        return base_trust * method_factor * corroboration_factor
    
    def _count_corroborating_sources(self, claim: Claim) -> int:
        """Count independent sources supporting claim"""
        pass
```

### 5.4 Forcing Engine

```python
class ForcingResult(Enum):
    ACCEPTED = "accepted"
    REJECTED_INCONSISTENT = "rejected_inconsistent"
    REJECTED_INSUFFICIENT = "rejected_insufficient"
    REJECTED_DOWNSTREAM = "rejected_downstream"
    PENDING = "pending"

@dataclass
class ForcingOutcome:
    result: ForcingResult
    claim_id: Optional[str] = None
    reason: str = ""
    conflicts: List[str] = None
    implications: List[str] = None

class ForcingEngine:
    """Principled knowledge extension"""
    
    def force(self, claim: Claim, evidence: List[Source]) -> ForcingOutcome:
        """Attempt to add claim to knowledge base"""
        
        # 1. Consistency check
        conflicts = self.registry.find_contradictions(claim)
        established_conflicts = [c for c in conflicts 
                                if c.status == EpistemicStatus.ESTABLISHED]
        
        if established_conflicts:
            return ForcingOutcome(
                result=ForcingResult.REJECTED_INCONSISTENT,
                reason="Contradicts established claims",
                conflicts=[c.id for c in established_conflicts]
            )
        
        # 2. Evidence evaluation
        evidence_strength = self._evaluate_evidence(evidence)
        
        if evidence_strength < self.config.min_evidence_threshold:
            return ForcingOutcome(
                result=ForcingResult.REJECTED_INSUFFICIENT,
                reason=f"Evidence strength {evidence_strength:.2f} below threshold"
            )
        
        # 3. Tentative addition
        claim.status = EpistemicStatus.HYPOTHESIZED
        claim.confidence = evidence_strength
        tentative_id = self.registry.add(claim)
        
        # 4. Derive implications
        implications = self._derive_implications(claim)
        
        # 5. Check implications for conflicts
        downstream_conflicts = []
        for imp in implications:
            imp_conflicts = self.registry.find_contradictions(imp)
            if any(c.status == EpistemicStatus.ESTABLISHED for c in imp_conflicts):
                downstream_conflicts.extend(imp_conflicts)
        
        if downstream_conflicts:
            self.registry.delete(tentative_id)  # Rollback
            return ForcingOutcome(
                result=ForcingResult.REJECTED_DOWNSTREAM,
                reason="Implications conflict with established claims",
                conflicts=[c.id for c in downstream_conflicts]
            )
        
        # 6. Commit
        if evidence_strength > self.config.established_threshold:
            self.registry.update_status(
                tentative_id, 
                EpistemicStatus.ESTABLISHED,
                "High evidence threshold met"
            )
        
        # Add implications
        implication_ids = []
        for imp in implications:
            imp.status = EpistemicStatus.HYPOTHESIZED
            imp_id = self.registry.add(imp)
            implication_ids.append(imp_id)
        
        return ForcingOutcome(
            result=ForcingResult.ACCEPTED,
            claim_id=tentative_id,
            implications=implication_ids
        )
    
    def _evaluate_evidence(self, evidence: List[Source]) -> float:
        """Compute aggregate evidence strength"""
        if not evidence:
            return 0.0
        
        scores = [self.trust_graph.propagate_trust(e) for e in evidence]
        
        # Diminishing returns for multiple sources
        sorted_scores = sorted(scores, reverse=True)
        weighted = sum(s * (0.7 ** i) for i, s in enumerate(sorted_scores))
        normalized = min(1.0, weighted / 2.0)
        
        return normalized
    
    def _derive_implications(self, claim: Claim) -> List[Claim]:
        """Derive logical implications from claim"""
        # Use inference rules + LLM for natural language implications
        pass
```

---

## 6. Runtime Layer APIs

### 6.1 Query Parser

```python
class QueryType(Enum):
    FACTUAL = "factual"           # What is X?
    EPISTEMIC = "epistemic"       # Is X known?
    PROCEDURAL = "procedural"     # How to X?
    COMPARATIVE = "comparative"   # X vs Y?
    CAUSAL = "causal"             # Why X?

@dataclass
class ParsedQuery:
    original: str
    type: QueryType
    concepts: List[str]
    relations: List[str]
    constraints: Dict[str, Any]

class QueryParser:
    def parse(self, query: str) -> ParsedQuery:
        """Parse natural language query into structured form"""
        pass
```

### 6.2 Inference Engine

```python
@dataclass
class InferenceResult:
    answer: str
    status: EpistemicStatus
    confidence: float
    supporting_claims: List[str]
    gaps_encountered: List[Gap]
    trace: List[str]  # Reasoning steps

class InferenceEngine:
    def infer(self, query: ParsedQuery) -> InferenceResult:
        """Answer query with epistemic awareness"""
        
        # 1. Direct lookup
        direct = self.registry.query(content=query.original)
        if direct and direct[0].status == EpistemicStatus.ESTABLISHED:
            return InferenceResult(
                answer=direct[0].content,
                status=EpistemicStatus.ESTABLISHED,
                confidence=direct[0].confidence,
                supporting_claims=[direct[0].id],
                gaps_encountered=[],
                trace=["Direct lookup successful"]
            )
        
        # 2. Check for contradiction
        contradictions = self.registry.find_contradictions_for_query(query)
        if contradictions:
            return InferenceResult(
                answer=self._format_contested(contradictions),
                status=EpistemicStatus.CONTESTED,
                confidence=0.5,
                supporting_claims=[c.id for c in contradictions],
                gaps_encountered=[],
                trace=["Found contested positions"]
            )
        
        # 3. Check for known unknown
        if self._is_known_unknown(query):
            return InferenceResult(
                answer=self._format_unknown(query),
                status=EpistemicStatus.UNKNOWN,
                confidence=0.0,
                supporting_claims=[],
                gaps_encountered=[],
                trace=["Identified as known unknown"]
            )
        
        # 4. Attempt derivation
        derivation = self._derive(query)
        if derivation:
            return derivation
        
        # 5. Acknowledge uncertainty
        gaps = self.gap_detector.detect_for_query(query.original)
        return InferenceResult(
            answer="I don't have established knowledge about this.",
            status=EpistemicStatus.UNKNOWN,
            confidence=0.0,
            supporting_claims=[],
            gaps_encountered=gaps,
            trace=["No established knowledge or derivation found"]
        )
```

### 6.3 Output Generator

```python
class OutputGenerator:
    """Generate responses respecting epistemic status"""
    
    def generate(self, result: InferenceResult) -> str:
        """Generate natural language response"""
        
        if result.status == EpistemicStatus.ESTABLISHED:
            return self._generate_confident(result)
        
        elif result.status == EpistemicStatus.CONTESTED:
            return self._generate_balanced(result)
        
        elif result.status == EpistemicStatus.UNKNOWN:
            return self._generate_uncertain(result)
        
        else:
            return self._generate_tentative(result)
    
    def _generate_confident(self, result: InferenceResult) -> str:
        """Generate confident response for established claims"""
        return result.answer
    
    def _generate_balanced(self, result: InferenceResult) -> str:
        """Present multiple positions for contested claims"""
        return f"This is a contested topic. {result.answer}"
    
    def _generate_uncertain(self, result: InferenceResult) -> str:
        """Acknowledge uncertainty for unknowns"""
        return f"This is genuinely unknown. {result.answer}"
    
    def _generate_tentative(self, result: InferenceResult) -> str:
        """Hedge for hypothesized claims"""
        return f"Based on current hypotheses: {result.answer}"
```

---

## 7. Configuration

```yaml
# onto_os_config.yaml

epistemic:
  min_evidence_threshold: 0.3
  established_threshold: 0.8
  stale_claim_days: 365
  max_inference_depth: 5

trust:
  default_source_trust: 0.5
  peer_reviewed_bonus: 0.2
  retraction_penalty: 0.3
  citation_factor: 0.01

storage:
  neo4j:
    uri: bolt://localhost:7687
    user: neo4j
    password: ${NEO4J_PASSWORD}
  
  qdrant:
    host: localhost
    port: 6333
  
  postgres:
    uri: postgresql://localhost/onto_os
  
  redis:
    host: localhost
    port: 6379

llm:
  provider: anthropic
  model: claude-3-opus
  temperature: 0.0
  max_tokens: 4096
```

---

## 8. Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  onto-os:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CONFIG_PATH=/app/config.yaml
    depends_on:
      - neo4j
      - qdrant
      - postgres
      - redis

  neo4j:
    image: neo4j:5.0
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=onto_os
      - POSTGRES_PASSWORD=${PG_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  neo4j_data:
  qdrant_data:
  pg_data:
```

---

## 9. API Reference

### REST API

```
POST /v1/claims
  Add new claim
  Body: Claim JSON
  Returns: claim_id

GET /v1/claims/{id}
  Retrieve claim
  Returns: Claim JSON

POST /v1/query
  Query knowledge base
  Body: { "query": "..." }
  Returns: InferenceResult JSON

POST /v1/force
  Force new claim
  Body: { "claim": Claim, "evidence": [Source] }
  Returns: ForcingOutcome JSON

GET /v1/gaps
  List all gaps
  Returns: [Gap JSON]

GET /v1/health
  Health check
  Returns: { "status": "ok" }
```

### Python SDK

```python
from onto_os import Client

client = Client(base_url="http://localhost:8000")

# Add claim
claim = client.claims.add(
    content="Water boils at 100°C at sea level",
    status="ESTABLISHED",
    domain="physics"
)

# Query
result = client.query("At what temperature does water boil?")
print(result.answer)  # "Water boils at 100°C at sea level"
print(result.status)  # ESTABLISHED

# Force new claim
outcome = client.force(
    claim={"content": "New finding..."},
    evidence=[source1, source2]
)
```

---

## 10. Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| v0.1 | Q1 2026 | Claim registry, basic forcing |
| v0.2 | Q2 2026 | Gap detection, trust graph |
| v0.3 | Q3 2026 | Inference engine, SDK |
| v1.0 | Q4 2026 | Production release |
| v1.1 | Q1 2027 | Multi-domain, federation |
| v2.0 | Q2 2027 | Distributed, real-time |

---

*ONTO-OS Technical Specification v1.0*
*January 2026*
