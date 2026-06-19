#!/usr/bin/env python3
# verify_lock_labels_v1.py -- RUNG-1 STEP 1c-iii: validate Founder labels + md5-lock the ground truth.
#
# AUTO (objective, auditable rule -- NOT a judgment): resolves=NO -> DIRTY / FAB_NORESOLVE.
#   A non-resolving DOI is a fabricated locator BY DEFINITION (DESIGN 5.1) -- Crossref 404 is a fact.
# FOUNDER-REQUIRED (independent semantic call): every resolves=YES row MUST carry founder_label +
#   reason_category. The script REFUSES to lock if any resolving row is unlabeled. This keeps the
#   support-judgment human + independent of the verifier's title-match (else rho-VOID is an artifact).
#
# Consistency enforced (R17): CLEAN <=> reason CLEAN ; DIRTY <=> reason in {FAB_NORESOLVE, WRONG_BIND,
#   NON_SUPPORT}. n>=30 DIRTY required (G-RUNG1 sample floor, DESIGN 5.3).
#
# Emits labels_locked_v1.jsonl ({id, doi, resolves, founder_label, reason_category}) + prints md5 and a
# LABEL-SIDE rho preview (how much of DIRTY is resolution-explained vs resolved-but-dirty). NOTE: the
# REAL rho (verifier-reject vs label) is computed at STEP 4 on the live intake -- this is only a preview.
#
# LOCAL-ONLY: the locked labels ARE the held-out ground truth -- never public git (3.2).
#
# Run (LOCAL, no network):
#   python verify_lock_labels_v1.py --worksheet data/label_worksheet_v1.csv --out data/labels_locked_v1.jsonl

import argparse, csv, hashlib, json, sys

VALID_LABEL = {"CLEAN", "DIRTY"}
DIRTY_REASONS = {"FAB_NORESOLVE", "WRONG_BIND", "NON_SUPPORT"}
CLEAN_REASONS = {"CLEAN"}


def norm(s):
    return (s or "").strip().upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worksheet", default="data/label_worksheet_v1.csv")
    ap.add_argument("--out", default="data/labels_locked_v1.jsonl")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.worksheet, encoding="utf-8-sig")))
    print("[load] %d rows from %s" % (len(rows), args.worksheet), file=sys.stderr)

    errors, locked = [], []
    auto_fab = 0
    for r in rows:
        rid = r["id"]
        res = norm(r["resolves"])
        lab = norm(r["founder_label"])
        rsn = norm(r["reason_category"])

        # AUTO objective: non-resolving -> FAB_NORESOLVE / DIRTY (definitional, not a judgment)
        if res == "NO":
            if lab and (lab != "DIRTY" or rsn not in ("", "FAB_NORESOLVE")):
                errors.append("%s: resolves=NO but labeled %s/%s (must be DIRTY/FAB_NORESOLVE)"
                              % (rid, lab, rsn))
                continue
            lab, rsn = "DIRTY", "FAB_NORESOLVE"
            auto_fab += 1
        elif res == "ERR":
            errors.append("%s: resolves=ERR -- re-run Crossref for this row before locking" % rid)
            continue
        else:  # resolves == YES -> Founder MUST have judged
            if lab not in VALID_LABEL:
                errors.append("%s: resolves=YES but founder_label=%r (need CLEAN|DIRTY)" % (rid, lab or ""))
                continue
            if lab == "CLEAN" and rsn not in CLEAN_REASONS:
                errors.append("%s: CLEAN needs reason_category=CLEAN (got %r)" % (rid, rsn or ""))
                continue
            if lab == "DIRTY" and rsn not in DIRTY_REASONS:
                errors.append("%s: DIRTY needs reason in %s (got %r)" % (rid, sorted(DIRTY_REASONS), rsn or ""))
                continue

        locked.append({"id": rid, "doi": r["doi"], "resolves": res,
                       "founder_label": lab, "reason_category": rsn})

    if errors:
        print("[STOP] %d validation errors -- fix the worksheet, do NOT lock:" % len(errors), file=sys.stderr)
        for e in errors[:40]:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)

    dirty = [x for x in locked if x["founder_label"] == "DIRTY"]
    clean = [x for x in locked if x["founder_label"] == "CLEAN"]
    from collections import Counter
    reasons = Counter(x["reason_category"] for x in locked)

    if len(dirty) < 30:
        print("[STOP] only %d DIRTY (need n>=30 for G-RUNG1). Over-provision more prompts and re-run."
              % len(dirty), file=sys.stderr)
        sys.exit(1)

    with open(args.out, "w", encoding="utf-8") as f:
        for x in locked:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    md5 = hashlib.md5(open(args.out, "rb").read()).hexdigest()

    # label-side L4-reach preview. The verifier's L1 = existence AND title-match. So both FAB_NORESOLVE
    # (no existence) and WRONG_BIND (title mismatch) are L1-rejected and NEVER reach L4. Only NON_SUPPORT
    # (resolved + on-topic title, fails on support) can pass L1 and reach the L4 contradiction-veto --
    # those are the non-circular core that actually tests curated->live transfer. (Approximate: the real
    # L1 title-match Jaccard is the verifier's at STEP 2/3; the real rho is computed at STEP 4.)
    n_fab = reasons.get("FAB_NORESOLVE", 0)
    n_wb = reasons.get("WRONG_BIND", 0)
    n_ns = reasons.get("NON_SUPPORT", 0)
    print("[LOCKED] %d rows -> %s  md5=%s" % (len(locked), args.out, md5), file=sys.stderr)
    print("[breakdown] DIRTY=%d (FAB=%d, WRONG_BIND=%d, NON_SUPPORT=%d) | CLEAN=%d | auto-FAB=%d"
          % (len(dirty), n_fab, n_wb, n_ns, len(clean), auto_fab), file=sys.stderr)
    print("[L4-reach preview] L1-rejected dirty (FAB+WRONG_BIND)=%d | L4-reaching dirty (NON_SUPPORT)=%d"
          % (n_fab + n_wb, n_ns), file=sys.stderr)
    if n_ns == 0:
        print("  WARNING: 0 NON_SUPPORT -- every dirty fails L1 (no existence or title mismatch), none"
              "\n  reaches the L4 contradiction-veto. At STEP 4 rho(reject, L1-bind)->1 -> likely VOID"
              "\n  (the live proposer is too crude to test L4 transfer). REAL property + bankable negative,"
              "\n  NOT a failure to fix and NOT a gate to tune.", file=sys.stderr)
    else:
        print("  %d NON_SUPPORT dirty pass L1 and reach L4 -- the non-circular core of fa_live." % n_ns,
              file=sys.stderr)
    print("NEXT: STEP 2 -- wire proposer -> FROZEN intake; verifier disposes BLIND; join these labels at STEP 4.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
