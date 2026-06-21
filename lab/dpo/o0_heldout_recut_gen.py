#!/usr/bin/env python3
"""
o0_heldout_recut_gen.py  --  fresh held-out for the denominator RE-CUT (SPEC_denominator_recut_v1).

WHY base, not post_lora: the S4 adapter is rolled back -> the LIVE organism-0 distribution is the
BASE proposer (generate_claim, Ollama qwen2.5-coder:7b, raw /api/generate, no LoRA), NOT
o0_learner.generate_heldout (which forces the rolled-back adapter). Spec 4.1 = live distribution.

E15-SAFE: emits claims with founder_label EMPTY. Claude authors NO CLEAN/DIRTY labels. Founder fills
them in to produce recut_labeled.jsonl.

Run (LOCAL, Ollama loaded; gen-only, ~minutes):
  python o0_heldout_recut_gen.py --k 2 --out eval/o0/o0_recut_candidates.jsonl
Dry-run (no Ollama):
  python o0_heldout_recut_gen.py --dry-run
"""
import argparse, json, sys, time
from datetime import datetime, timezone

# same modules the live cycle uses -- import, do not reimplement
from rung1_wiring_v0 import generate_claim, ollama_generate
from o0_domain_list import HELD_OUT_TOPICS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=2,
                    help="claims per held-out topic (20 topics x k). k=2 -> 40 candidates")
    ap.add_argument("--out", default="eval/o0/o0_recut_candidates.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    target = len(HELD_OUT_TOPICS) * a.k
    print("[gen] held-out topics: %d  x k=%d  -> target %d candidates"
          % (len(HELD_OUT_TOPICS), a.k, target))
    print("[gen] generator: BASE proposer (generate_claim, no LoRA)  source=base_proposer")

    if a.dry_run:
        with open(a.out, "w", encoding="utf-8") as f:
            for i, t in enumerate(HELD_OUT_TOPICS):
                for k in range(a.k):
                    f.write(json.dumps({"id": "heldout_re_%02d" % (i * a.k + k),
                                        "topic": t, "k": k, "claim": "",
                                        "source": "base_proposer", "founder_label": ""}) + "\n")
        print("[gen] DRY RUN -> %d empty rows -> %s" % (target, a.out))
        return

    # pre-flight: Ollama reachable
    try:
        ollama_generate("Say OK", timeout=15)
    except Exception as e:
        sys.exit("FATAL: Ollama not reachable -- %s (load qwen2.5-coder:7b)" % e)

    rows, seen, dups = [], set(), 0
    t0 = time.time()
    idx = 0
    for i, topic in enumerate(HELD_OUT_TOPICS):
        for k in range(a.k):
            try:
                claim = generate_claim(topic)
            except Exception as e:
                print("[gen] WARN topic %d k%d proposer error: %s" % (i, k, e))
                claim = ""
            key = claim.strip()
            is_dup = key in seen and key != ""
            if is_dup:
                dups += 1
            else:
                seen.add(key)
            rows.append({"id": "heldout_re_%02d" % idx, "topic": topic, "k": k,
                         "claim": claim, "source": "base_proposer",
                         "founder_label": "", "dup": is_dup})
            idx += 1
            print("[%d/%d] %s%s" % (idx, target, topic[:48],
                                    "  [DUP]" if is_dup else ""))

    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    non_empty = sum(1 for r in rows if r["claim"].strip())
    unique = sum(1 for r in rows if not r["dup"] and r["claim"].strip())
    elapsed = time.time() - t0
    print("\n[gen] wrote %d rows -> %s" % (len(rows), a.out))
    print("[gen] non-empty %d  unique %d  exact-dups %d  elapsed %.0fs"
          % (non_empty, unique, dups, elapsed))
    if unique < 40:
        print("[gen] WARN unique < 40 -- raise --k or add HELD_OUT_TOPICS before labeling")
    print("[gen] NEXT (Founder, E15): fill founder_label CLEAN/DIRTY -> recut_labeled.jsonl")
    print("[gen] timestamp %s" % datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    main()
