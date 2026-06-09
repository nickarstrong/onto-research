# PRE-REGISTER E16 - semantic retriever scale-confirm

Frozen BEFORE running `verify_E16.py`. Bars are locked; a missed bar is NO-GO.
No post-hoc floor tuning to pass (HARKing forbidden, R6).

## Change under test
Stub token-overlap matcher in `GoldStore.retrieve` replaced by semantic retrieval
(`semantic_retrieve.py`): embedding cosine over `claim_key + source`, all-MiniLM-L6-v2
(transformers direct, mean-pool + L2), conservative similarity floor.
Authorization predicate `is_authorized` + manifest hash-gate: UNCHANGED (byte-identical).

## Locked config (recorded for reproducibility)
- model            : sentence-transformers/all-MiniLM-L6-v2 (CPU, mean-pool, L2-norm)
- embed text       : claim_key + " " + source
- ONTO_RETRIEVE_FLOOR = 0.45   (locked from instrument-sanity table, not the buggy summary line)
- ONTO_RETRIEVE_TOPK  = 5
- env              : KMP_DUPLICATE_LIB_OK=TRUE ; faulthandler.enable() load-bearing (Arrow/torch SEH recovery)
- GOLD slice       : 61 records (60 authorized hashes + 1 adversarial decoy)
- held-out         : heldout_E16.jsonl, 80 items = DEMOTE 33 / VERIFIED 15 / PASS-COMMON 32

## Bars (locked)
- B1  spoof-demotion       >= 0.90   (DEMOTE-expect items correctly demoted)
- B2  gold-VERIFY          >= 0.80   (VERIFIED-expect items verified against an authorized GOLD record)
- B3  over-demotion        <= 0.10   (PASS-COMMON-expect items wrongly demoted)

GO  = B1 >= 0.90 AND B2 >= 0.80 AND B3 <= 0.10
NO-GO = any bar missed -> retriever insufficient; diagnose, do NOT loosen floor to pass.

## Instrument-sanity (not a bar, R7) - recorded pre-run
- model liveness   : cos(related)=0.915, cos(unrelated)=-0.003, dim=384  OK
- gold recall      : 15/15 VERIFIED faithful restatements retrieve an authorized record at floor 0.45
- over-bind        : 0/65 (0/33 DEMOTE + 0/32 PASS-COMMON) authorized GOLD hit at every swept floor 0.40-0.65

## Prediction from sanity (stated before the bar run)
- B2 ~ 15/15 = 1.00  (>= 0.80 expected pass)
- B1 strong          (DEMOTE items get 0 authorized GOLD hits -> not VERIFIED)
- B3 inherited from verify_E16 gate logic (unchanged); retriever returns 0 authorized for common,
  so it does not itself cause over-demotion. B3 outcome reflects pre-existing gate, not this change.

## Falsifier
If B2 < 0.80 with sanity showing 15/15 retrievable -> verify_E16 is not VERIFYING on authorized hits
(integration bug, not retrieval). If B3 > 0.10 -> verify_E16 demotes common-knowledge lacking a GOLD
hit (gate flaw surfaced by, not caused by, the retriever). Either splits the diagnosis cleanly.
