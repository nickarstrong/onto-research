# PREREG v282 - CONDITIONED-RUN VALIDATION (SEALED before run)

Frozen: falsifier-first. No goalpost movement post-run. HEAD anchor at seal = 595e140.

## SUBSTRATE (verified on-disk, cross-machine md5)
| artifact | md5 | role |
|---|---|---|
| o0_verdicts.jsonl              | 91f442a0 | CANONICAL pool (ABSORB 187 / REJECT 87 / ABSTAIN 86) |
| o0_verdicts_c2migrated.jsonl   | e886bc2a | c2 CANDIDATE (ABSORB 176 / REJECT 87 / ABSTAIN 97; +11 ABSORB->ABSTAIN) |
| o0_temporal_evidence.py        | 92766b06 | FROZEN verifier (oracle proof-source; NOT on proposer feed) |

## FEED + QUARANTINE (sealed)
- PROPOSER feed = `o0_retrieve.load_confirmed(candidate)` = ABSORB-only + pool-hygiene
  (`_materialised OR _materialised_year`). Count = **176**.
- `load_confirmed(canonical) == load_confirmed(candidate)` = **176 == 176** (byte-identical at
  load layer) => retrieve-path firewall already quarantines the same 11 the c2 flip moves in the
  conditioning path. Cross-consumer consistency holds at the source.
- Quarantine set Q97 = candidate-ABSTAIN = **97** ids = 11 c2-flip (disjoint) + 86 prior-ABSTAIN.
  Q97 sorted-set md5 = **45259b37**. Per-row ids = LOCAL only (`v282_quarantine_ids.json`, R15).
- ENTRYPOINT (conditioned proposer) = `run_step6_live.py` (imports o0_retrieve + generate_step6 +
  falsifier_step6). Eval/rate path (`run_step7_live.py`) and verifier are separate.

## BARS (all GREEN -> pass; any RED -> fail)
STATIC (in-session, sealed now -- structurally guaranteed, NON-DISCRIMINATIVE; declared as such):
- S1  feed = load_confirmed(candidate) = 176; intersect(Q97) == empty.            [verified]
- S2  load_confirmed(canonical) == load_confirmed(candidate) == 176.              [verified]
- S3  o0_retrieve / load_confirmed NOT imported by the verifier path.             [verified: not in import set]
- S4  generate_step6 proposal keys == {topic, claim} (no id/ctx/gold leak).       [asserted falsifier_step6 L61]

RUN-LEVEL (RunPod GENERATE batch over the 176-feed -- the BINDING bars):
- R-EXCL  union(retrieved ids in v282_retrieve_audit.jsonl) intersect Q97 == empty.
          (catches a code-path BYPASS: raw-verdicts read, unfiltered retrieve, topic-collision route)
- R-MECH  >= 1 audit line with non-empty ids (mechanism EXERCISED; guards the v275 0-exercised trap).
- R-SEAL  Q97 sorted-set md5 == 45259b37 at falsifier run.

HONEST CAVEAT (R17): S1-S2 are a load-layer tautology (ABSORB-only filter, Q97 in ABSTAIN). They are
NOT discrimination. The run is discriminative ONLY via R-MECH (proves the conditioned arm actually
retrieved) + R-EXCL-as-bypass-trap. The tap (`o0_retrieve_tap.py`) exists because the generator
firewall strips retrieved ids from proposals (generate_step6 L76/L89), so without a side-channel audit
R-EXCL would be unfalsifiable.

## FALSIFIER-OF-FALSIFIER (proven before seal)
`falsifier_v282_quarantine.py`: CLEAN audit -> GREEN; injected Q97 id -> RED (R-EXCL);
empty audit -> RED (R-MECH). Discrimination confirmed.

## RUN WIRING (RunPod; proposer side only)
```
import o0_retrieve as R
from o0_retrieve_tap import tapped_retrieve
confirmed   = R.load_confirmed("eval/o0/o0_verdicts_c2migrated.jsonl")   # = 176
retrieve_fn = tapped_retrieve(R.retrieve, "eval/o0/v282_retrieve_audit.jsonl")
# generate_step6.generate(..., confirmed=confirmed, retrieve_fn=retrieve_fn, gold_frame="", k=...)
python falsifier_v282_quarantine.py --audit eval/o0/v282_retrieve_audit.jsonl --q97 v282_quarantine_ids.json
```

## ON GREEN
273-bak (9cfe3e51) becomes sanctioned-deletable (rollback window closes). v280pre (755d81c3) stays one
more cycle. Canonical SWAP (91f442a0 -> e886bc2a) is the Founder-gated NEXT+1 decision, NOT this plane.
