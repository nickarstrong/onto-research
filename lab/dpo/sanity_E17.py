#!/usr/bin/env python3
"""sanity_E17.py - instrument-sanity for the E17 full-GOLD scale check (NOT a bar, R7).

Extends sanity_E16.py (repointed to heldout_E17 + 216-record fixture) with the
density-vs-degradation falsifier the keystone needs to attribute a NO-GO at scale.

Confirms, BEFORE frozen verify_E16 --eval and BEFORE pre-register:
  0. model liveness   : embeddings real (dim 384, related>unrelated).
  a. VERIFY recall    : gold-backed restatements retrieve an AUTHORIZED record.
  b. over-bind == 0   : DEMOTE-expect items retrieve NOTHING authorizable. This is the
                        precision constraint that LOCKS the floor (lowest floor, ob==0).
  c. score separation : top-1 cosine distribution VERIFY vs DEMOTE - do they separate?
  d. DENSITY CONTROL  : re-run over-bind at the locked floor on a 60-record subsample.
                        over-bind(216) > over-bind(60) => density-driven (floor re-lock
                        is correct, NOT verifier degradation). No floor kills ob on 216
                        while VERIFY recall holds => terminal (cheap-Entity path FALSE).
  e. gold unbiasedness: KS test, top-1 cosine of VERIFY held-out vs corpus NN baseline.
                        p>0.05 => gold sample not easier than corpus (no B2 inflation).

Run with `python` (Windows: not python3). Held-out + fixture read from eval/_local.
Env (load-bearing, sec 5): KMP_DUPLICATE_LIB_OK=TRUE ; faulthandler in semantic_retrieve.
"""
import json, os, sys, math, bisect
from collections import defaultdict

from gold_retrieve import GoldStore
import semantic_retrieve as sr

HELDOUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "eval", "_local", "heldout_E17.jsonl")
FLOORS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
SUBSAMPLE_N = 60                      # density control: E16-era corpus size
_VALID_EXPECT = {"VERIFY", "DEMOTE"}  # sec-6 guard: VERIFY/VERIFIED confusion fails loud


def model_liveness():
    rel = sr._embed(["error threshold in replication", "the error threshold of replication"])
    unrel = sr._embed(["error threshold in replication", "a recipe for chocolate cake"])
    dim = rel.shape[1]
    cos_rel, cos_unrel = float(rel[0] @ rel[1]), float(unrel[0] @ unrel[1])
    ok = dim == 384 and cos_rel > cos_unrel and cos_rel > 0.5
    print(f"[0] LIVENESS dim={dim} cos(related)={cos_rel:.3f} cos(unrelated)={cos_unrel:.3f} "
          f"-> {'OK' if ok else 'FAIL'}")
    if not ok:
        sys.exit("MODEL LIVENESS FAILED - embeddings not real; fix before sanity.")


def load_heldout():
    items = []
    with open(HELDOUT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    bad = sorted({it.get("expect", "?") for it in items} - _VALID_EXPECT)
    if bad:
        sys.exit(f"HELD-OUT expect vocabulary invalid: {bad} (must be {_VALID_EXPECT}). "
                 f"Sec-6 guard: a VERIFY/VERIFIED typo silently zeros recall - fix the data.")
    return items


def ks_2samp(a, b):
    """Two-sample KS (manual; no scipy). Returns (D, p_asymptotic)."""
    a, b = sorted(a), sorted(b)
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return float("nan"), float("nan")
    grid = sorted(set(a + b))
    D = max(abs(bisect.bisect_right(a, v) / n - bisect.bisect_right(b, v) / m) for v in grid)
    en = math.sqrt(n * m / (n + m))
    lam = (en + 0.12 + 0.11 / en) * D
    p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * lam * lam * k * k) for k in range(1, 101))
    return D, max(0.0, min(1.0, p))


def top1_auth_cosine(text, records, manifest):
    """Top-1 cosine among AUTHORIZED candidates (hash in manifest); None if none in top_k."""
    for cos, _src, loc, h in sr.scores(text, records):
        if h in manifest and loc:
            return cos
    return None


def top1_cosine(text, records):
    sc = sr.scores(text, records)
    return sc[0][0] if sc else None


def over_bind(items, records, manifest, floor):
    obs = []
    for it in items:
        if it.get("expect") != "DEMOTE":
            continue
        hits = sr.retrieve(it["text"], records, floor=floor)
        if any(h["hash"] in manifest and h["locator"] for h in hits):
            obs.append(it["id"])
    return obs


def verify_recall(items, records, manifest, floor):
    ok = 0
    tot = 0
    for it in items:
        if it.get("expect") != "VERIFY":
            continue
        tot += 1
        hits = sr.retrieve(it["text"], records, floor=floor)
        if any(h["hash"] in manifest and h["locator"] for h in hits):
            ok += 1
    return ok, tot


def main():
    store = GoldStore()
    recs, mf = store.records, store.manifest_files
    print(f"GOLD full: {len(recs)} records, {len(mf)} authorized hashes")
    model_liveness()

    items = load_heldout()
    by_expect = defaultdict(int)
    for it in items:
        by_expect[it["expect"]] += 1
    print(f"held-out: {len(items)} items  by expect={dict(by_expect)}")

    # --- [a/b] floor sweep on full 216 -> lock floor (lowest ob==0, max VERIFY recall) ---
    print("\n[floor sweep / full 216]  authorized-hit rate per expect | over-bind on DEMOTE")
    print(f"{'floor':>6} | " + " | ".join(f"{e:>7}" for e in sorted(by_expect)) + " | overbind")
    best = None
    per_floor = {}
    for fl in FLOORS:
        sr._index = None
        authok = defaultdict(int)
        obs = []
        for it in items:
            hits = sr.retrieve(it["text"], recs, floor=fl)
            if any(h["hash"] in mf and h["locator"] for h in hits):
                authok[it["expect"]] += 1
                if it["expect"] == "DEMOTE":
                    obs.append(it["id"])
        per_floor[fl] = (dict(authok), obs)
        rates = " | ".join(f"{authok[e]}/{by_expect[e]:>5}" for e in sorted(by_expect))
        print(f"{fl:>6.2f} | {rates} | {len(obs)}")
        if len(obs) == 0 and (best is None or authok.get("VERIFY", 0) > best[1]):
            best = (fl, authok.get("VERIFY", 0))

    print("\n[over-bind detail] (DEMOTE items with an AUTHORIZED hit - empty at locked floor)")
    for fl in FLOORS:
        ob = per_floor[fl][1]
        print(f"  floor={fl:.2f}: {ob if ob else 'none'}")

    if not best:
        print("\nNO floor in sweep achieves over-bind==0 -> tighten FLOORS upward and re-sweep "
              "(do NOT loosen toward eval). If even 0.65 fails: see [d] - terminal candidate.")
        locked = None
    else:
        locked = best[0]
        print(f"\nRECOMMENDED floor (lowest ob==0, max VERIFY recall): {locked:.2f} "
              f"(VERIFY authorized {best[1]}/{by_expect['VERIFY']})")
        print(f"  -> set:  $env:ONTO_RETRIEVE_FLOOR = \"{locked:.2f}\"   before pre-register + eval")

    fl_diag = locked if locked is not None else FLOORS[-1]

    # --- [c] score separation: top-1 cosine VERIFY vs DEMOTE -----------------------------
    sr._index = None
    v_cos = [c for it in items if it["expect"] == "VERIFY"
             for c in [top1_cosine(it["text"], recs)] if c is not None]
    d_cos = [c for it in items if it["expect"] == "DEMOTE"
             for c in [top1_cosine(it["text"], recs)] if c is not None]
    def stat(x):
        x = sorted(x)
        return (f"min={x[0]:.3f} med={x[len(x)//2]:.3f} max={x[-1]:.3f}") if x else "n/a"
    print(f"\n[c] top-1 cosine separation @floor-agnostic")
    print(f"  VERIFY : {stat(v_cos)}")
    print(f"  DEMOTE : {stat(d_cos)}")
    print(f"  -> separated (DEMOTE max < VERIFY med) means a floor can split them; "
          f"heavy overlap => no floor separates => scale-terminal signal.")

    # --- [d] DENSITY CONTROL: over-bind at locked floor, 216 vs 60-subsample -------------
    # subsample preserves VERIFY targets (recall held), deterministic fill by hash sort.
    sr._index = None
    needed = set()
    for it in items:
        if it["expect"] != "VERIFY":
            continue
        for h in sr.retrieve(it["text"], recs, floor=fl_diag):
            if h["hash"] in mf and h["locator"]:
                needed.add(h["hash"])
    by_hash = {r["hash"]: r for r in recs}
    sub = [by_hash[h] for h in needed if h in by_hash]
    fill = [r for r in sorted(recs, key=lambda r: r["hash"]) if r["hash"] not in needed]
    sub += fill[:max(0, SUBSAMPLE_N - len(sub))]
    sr._index = None
    ob_full = over_bind(items, recs, mf, fl_diag)
    sr._index = None
    ob_sub = over_bind(items, sub, mf, fl_diag)
    sr._index = None
    vr_sub = verify_recall(items, sub, mf, fl_diag)
    print(f"\n[d] DENSITY CONTROL @floor={fl_diag:.2f}")
    print(f"  corpus 216 : over-bind={len(ob_full)}  {ob_full if ob_full else ''}")
    print(f"  corpus {len(sub):>3} : over-bind={len(ob_sub)}  VERIFY-recall(subset)={vr_sub[0]}/{vr_sub[1]}")
    if len(ob_full) > len(ob_sub):
        print("  -> over-bind grows with corpus size => DENSITY-DRIVEN. Floor re-lock is the "
              "correct response; not verifier degradation.")
    elif len(ob_full) == len(ob_sub) and len(ob_full) > 0:
        print("  -> over-bind size-invariant => NOT density; floor/verifier issue. Diagnose "
              "before any tuning.")
    else:
        print("  -> over-bind==0 at both sizes => clean at locked floor.")

    # --- [e] gold-sample unbiasedness: KS(VERIFY top-1 cosine, corpus NN baseline) -------
    sr._index = None
    # corpus NN baseline: each record's nearest non-self neighbour cosine
    base = []
    for r in recs:
        sc = sr.scores(r["claim_key"] + " " + r["source"], recs)
        nn = next((c for c, s, l, h in sc if s[:40] != r["source"][:40]), None)
        if nn is not None:
            base.append(nn)
    D, p = ks_2samp([c for c in v_cos], base)
    print(f"\n[e] gold unbiasedness  KS(VERIFY top-1, corpus-NN)  D={D:.3f} p={p:.3f}")
    print(f"  -> p>0.05: gold sample NOT easier than corpus (no B2 inflation). "
          f"p<=0.05 with VERIFY shifted high => easy-biased; replace easy gold with hard.")


if __name__ == "__main__":
    main()
