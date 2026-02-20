# ONTO — AI Provider Licensing

**Document:** ONTO-LICENSING-PROVIDERS-2026  
**Version:** 1.0  
**Date:** 2026-02-20  
**Contact:** council@ontostandard.org

---

## What ONTO Is

ONTO is an epistemic discipline layer for AI models. It enforces structured reasoning: calibrated confidence, source citation, gap quantification, limitation disclosure.

You integrate GOLD once. Your model's epistemic behavior changes across all outputs. No retraining. No fine-tuning. No model access required.

---

## How Provider Integration Works

```
ONTO Server ──SSE stream──▸ Your Infrastructure
                                 │
                            cache in RAM
                                 │
                       inject into model pipeline
                                 │
                         serve your users
```

1. Connect to `/stream/connect` — receive GOLD corpus via SSE
2. Cache locally — your infrastructure, your control
3. Inject into system prompt pipeline — one-time setup
4. Heartbeat every 300s confirms active license

**ONTO is not in your inference path.** After initial sync, your latency = your latency.

---

## Provider License

### Standard — $120,000/yr
*We evaluate your model.*

- GOLD TIER 4 (Extended Corpus) via SSE stream
- Cache locally, inject unlimited — no per-request fees
- Up to 20 models
- Quarterly epistemic benchmark (100-question evaluation, published score)
- "ONTO Evaluated" badge
- 12-month audit trail
- Email support

### Enterprise — $250,000/yr
*We certify your model.*

- GOLD TIER 6 (Full Corpus) via SSE stream
- Up to 100 models
- Monthly benchmark reports
- **"ONTO Certified" public certificate** — show to your enterprise clients
- Ed25519 signed verification endpoint — your clients verify independently
- 24-month audit trail
- Early access to GOLD updates
- Dedicated support + SLA

### Strategic Partner — $500,000+/yr
*We build the standard together.*

- Everything in Enterprise
- Unlimited models
- **White-label certification** — brand as your own quality layer
- Custom GOLD modules for your domain (medical, legal, finance)
- Advisory board seat
- Joint research publication rights
- Co-development of domain-specific scoring

---

**Fixed annual fee. No per-token, per-request, or per-user charges.**

At scale, ONTO cost approaches zero per request:

| Your daily volume | Standard ($120K/yr) | Enterprise ($250K/yr) |
|---|---|---|
| 100K req/day | $0.003/req | $0.007/req |
| 1M req/day | $0.0003/req | $0.0007/req |
| 10M req/day | $0.00003/req | $0.00007/req |

---

## Your Cost Structure

| Component | Cost |
|-----------|------|
| ONTO license | $120K–$250K/yr (fixed) |
| Token overhead per request | 0 (GOLD cached locally) |
| Compute overhead | Negligible (KV cache reuse) |
| Bandwidth to ONTO | ~1 SSE burst + heartbeat/300s |
| Integration engineering | One-time, <1 day |

Your model serves 10K or 10M requests/day — your ONTO cost is identical.

---

## What Changes In Your Model's Output

Measured across 11 baseline models, 100 questions, deterministic scoring, zero AI judge:

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Composite score | 0.53 | 5.38 | 10× |
| Source citations | 0 per response | 3+ per response | New capability |
| Confidence calibration | Absent | Numerical (0.35, 0.80) | New capability |
| Over-confidence | Uncontrolled | Controlled | ↓ 35% |
| Output variance (SD) | 0.58 | 0.11 | 5.4× reduction |
| Cross-domain transfer | 0/5 | 4/5 | 80% |

No baseline model has calibrated confidence or gap quantification. ONTO adds both.

---

## Why This Matters For Your Business

**Enterprise procurement.** B2B clients increasingly require verifiable AI quality. ONTO certification is an independent, reproducible quality signal that shortens procurement cycles.

**Regulatory readiness.** EU AI Act requires transparency and accuracy reporting for high-risk AI. ONTO-certified models produce the audit artifacts regulators expect.

**Competitive differentiation.** In a market where model capabilities converge, epistemic discipline is the measurable differentiator. First provider with independent quality verification wins enterprise trust.

**Pricing power.** Verified epistemic quality justifies premium pricing. Your competitors claim quality. You prove it.

---

## Verification Architecture

- Deterministic scoring engine (993 lines, regex-based, zero AI judge)
- Ed25519 cryptographic proof chain (104 bytes per evaluation)
- Public verification endpoint
- Fully reproducible — same input produces identical score on any machine
- Open methodology on GitHub

---

## Founding Program

First 20 providers: pay 12 months, receive 24 months. Case study rights, quarterly advisory calls, roadmap influence.

---

## Next Step

Request an independent evaluation of your model's epistemic behavior.

**council@ontostandard.org**

---

*ONTO Standards Council · Est. 2024*  
*Independent research initiative.*
