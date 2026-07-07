#!/usr/bin/env python3
"""
concept_retrieval_margin_v439.py -- MARGIN-gated concept-triggered GOLD retrieval (INSTRUCT, QA).

Evolution of concept_retrieval_v437.py (SKILL 4: change representation, not logic).
v437 gated on absolute max-cosine (det_sim < TAU); PASS was FRAGILE -- bought by
false-abstaining F2h (correct-detect, sim .359 < tau) and blocking the two wrong-
detects by luck of absolute magnitude. v437 close: max-cosine does NOT discriminate
right-from-wrong (separability gap -0.0066, F7h wrong .366 > F2h correct .359).
v438 margin probe (PURE measurement, no gate): margin=top1-top2 separates cleanly,
gap +0.0104 (min correct-detect F2h .0309 > max wrong-detect F3h .0205); straddle
RESOLVED (F2h .0309 > F7h .0138). v439 BUILDS the margin-gate and tests DOMINANCE.

Inherited from v437 BYTE-FOR-BYTE (evolution = change representation, not logic):
  MODEL_ID, DATA_PATH, DETECT_LAYER, CLOZE_HELD, GOLD_FRAGMENTS, KEY, KEY_NEG_SI4,
  tok_id, get_hidden_at_layer, cosine_sim, cloze_to_question, answer_correct,
  build_user_content, generate_answer, the L13 centroid computation block,
  and the baseline/gated eval-loop STRUCTURE + boost/blocked/false-abstain metrics.
Inherited from v438 BYTE-FOR-BYTE:
  detect_concept_full (returns full sorted (si, sim) vector; detected_si = top1_si).
Changed representation ONLY:
  - gate variable: v437 `gated = det_sim < TAU`  ->  v439 `gated = margin < M`
    where margin = top1_sim - top2_sim (from detect_concept_full).
  - M = 0.025 (midpoint of v438 gap 0.0205 <-> 0.0309; pack v439 sec3, immutable).
  - PASS_BOOST = 5 (DOMINANCE bar: recover F2h -> boost 4/7 -> 5/7; v437 was 4).
  - eval loop records top1_sim/top2_sim/margin per held-out.
  - report: boost N/7, wrong-blocked N/2, false-abstain N, and EXPLICIT F2h transition
    (false-abstain@v437 -> boost@v439?).

DOMINANCE QUESTION (pack v439 sec2): does the margin-gate RECOVER F2h that max-cosine
false-abstained (boost 4/7 -> 5/7) WHILE still blocking both wrong-detects (F3h, F7h
margin < M)? Necessary, not sufficient -- N=7, m FIT to this set (v438 grub, OWED-
GENERALIZATION deferred v440+: needs a disjoint held-out split to test m transfer).

G3 FALSIFIER (pre-registered, pack v439 sec5, immutable):
  Under margin-gate M=0.025: mechanistic boost < 5/7 OR any wrong-detect passes the
  gate (margin >= M on F3h or F7h)
  -> margin-gate does NOT dominate the v437 max-cosine gate on the 7 held-out
  -> the margin geometric trigger yields no gain over max-cosine on this set
  -> close the geometric-trigger line; pivot to a NON-geometric retrieval trigger
     (retrieval-verification / abstain-by-agreement / answer-consistency).

v439 - TRACK 2 ORGANISM - retrieval trigger: MARGIN-gate.
Run: LOCAL RTX 4070 8GB, 4-bit NF4. 35 centroid + 7 detect fwd + <=14 gen(100tok). <2min, $0.
"""

import torch
import json, os, time

MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/margin_gate_v439.json"
DETECT_LAYER = 13
M = 0.025             # margin gate: margin(top1-top2) < M -> no-retrieve (baseline). pack v439 sec3, immutable.
PASS_BOOST = 5        # DOMINANCE: >=5/7 held-out mechanistic boost (recover F2h; v437 bar was 4)
MAX_NEW = 100

# -- GOLD fragments (identical to v434/v436/v437) --
GOLD_FRAGMENTS = {
    0: "Probability calculations against random self-replicator assembly are misleading because they assume modern protein complexity rather than simpler precursor molecules that could have initiated life.",
    1: "The fraction of random amino-acid sequences with simple biological function is roughly one in ten to the eleven, or approximately 10^-11, based on empirical studies of random polypeptide libraries.",
    2: "About a third of the 473 genes in JCVI-syn3.0, the minimal synthetic cell, have functions that remain unknown despite being essential for life.",
    3: "Eigen's error catastrophe describes the threshold where copying errors in prebiotic replication outpace natural selection, limiting the complexity of early replicators without enzymatic error correction.",
    4: "According to Totani (2020), the observable universe is not sufficient for random nucleotide assembly to produce a functional RNA replicase by chance alone.",
    5: "Shannon's information theory deliberately excludes the concept of meaning, measuring only statistical uncertainty of message transmission regardless of semantic content.",
    6: "The Cit+ phenotype in Lenski's long-term evolution experiment enabled E. coli to metabolize citrate under aerobic conditions, emerging after approximately 31,500 generations.",
}

# -- 7 held-out cloze prompts (identical to v434/v436/v437/v438) --
CLOZE_HELD = [
    {"id": "F1h", "prompt": "The standard argument against abiogenesis via random protein assembly is widely regarded as", "target": "misleading", "si": 0},
    {"id": "F2h", "prompt": "Among random polypeptides, the chance of any biological activity is about one in ten to the", "target": "eleven", "si": 1},
    {"id": "F3h", "prompt": "Many genes in the synthetic minimal cell have purposes that remain", "target": "unknown", "si": 2},
    {"id": "F4h", "prompt": "In Eigen's framework, replication collapses when mutations overwhelm", "target": "selection", "si": 3},
    {"id": "F5h", "prompt": "Is the observable universe large enough for chance formation of an RNA replicase?", "target": "No", "si": 4},
    {"id": "F6h", "prompt": "In his 1948 paper, Shannon chose to exclude", "target": "meaning", "si": 5},
    {"id": "F7h", "prompt": "Lenski's key evolutionary innovation was citrate metabolism under", "target": "aerobic", "si": 6},
]

# -- key-fact keywords per concept (identical to v436/v437, immutable) --
KEY = {
    0: ["misleading", "wrong reference", "flawed", "not as impossibly", "not impossibly"],
    1: ["eleven", "10^-11", "10^11", "10-11", "10^{-11}", "1e-11", "ten to the eleven"],
    2: ["unknown", "not known", "unclear", "not understood", "mysteri"],
    3: ["selection"],
    5: ["meaning", "semantic"],
    6: ["aerobic", "oxygen"],
}
KEY_NEG_SI4 = ["not sufficient", "not enough", "not large enough", "insufficient", "cannot", "too small", "not big enough"]


def cloze_to_question(cloze):
    s = cloze.strip()
    if s.endswith("?"):
        return s
    s = s.rstrip(" .,:;")
    q = s + " what?"
    return q[0].upper() + q[1:]


def answer_correct(si, answer):
    low = answer.lower()
    if si == 4:
        if any(k in low for k in KEY_NEG_SI4):
            return True
        first = low.strip().lstrip(".,!:*-\"' ")
        toks = first.split()
        return bool(toks) and toks[0].strip(".,!:") == "no"
    return any(k.lower() in low for k in KEY[si])


def tok_id(tokenizer, word):
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    if len(ids) > 1:
        if tokenizer.decode([ids[0]]).strip() == "":
            return ids[1]
    return ids[0]


def get_hidden_at_layer(model, tokenizer, prompt, layer):
    dev = next(model.parameters()).device
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    with torch.no_grad():
        out = model(ids, use_cache=False, output_hidden_states=True)
    return out.hidden_states[layer + 1][0, -1, :].float().cpu()


def cosine_sim(a, b):
    return torch.dot(a, b) / (a.norm() * b.norm() + 1e-8)


def build_user_content(question, gold_fragment=None):
    if gold_fragment is None:
        return f"<question>{question}</question>\nAnswer concisely."
    return (f"<context>{gold_fragment}</context>\n"
            f"<question>{question}</question>\n"
            f"Answer concisely based on the context above.")


def generate_answer(model, tokenizer, user_content):
    dev = next(model.parameters()).device
    msgs = [{"role": "user", "content": user_content}]
    text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tokenizer(text, return_tensors="pt").to(dev)
    in_len = ids.input_ids.shape[1]
    with torch.no_grad():
        gen = model.generate(**ids, max_new_tokens=MAX_NEW, do_sample=False,
                             temperature=None, top_p=None, top_k=None,
                             pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(gen[0][in_len:], skip_special_tokens=True).strip()


def main():
    assert torch.cuda.is_available(), "CUDA required"
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    lines = [json.loads(l) for l in open(DATA_PATH)]
    train_prompts, train_labels = [], []
    for si in range(7):
        group = [l for l in lines if l["source_idx"] == si][:5]
        for g in group:
            train_prompts.append(g["prompt"])
            train_labels.append(si)

    print("=" * 72)
    print("MARGIN-GATED RETRIEVAL v439 (organism, margin trigger)")
    print(f"Model: {MODEL_ID}")
    print(f"Detect layer: L{DETECT_LAYER}   M={M}")
    print(f"G3: boost >=5/7 AND both wrong-detects blocked (margin<M) else margin-gate not dominant")
    print("=" * 72)

    print("\n[1] Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True)
    model.eval()
    print(f"  {model.config.num_hidden_layers} layers, hidden={model.config.hidden_size}")

    # -- centroid computation: BYTE-IDENTICAL to v437 --
    print(f"\n[2] Computing concept centroids at L{DETECT_LAYER} (instruct geometry)...")
    t0 = time.time()
    centroid_vecs = {si: [] for si in range(7)}
    for i, prompt in enumerate(train_prompts):
        h = get_hidden_at_layer(model, tokenizer, prompt, DETECT_LAYER)
        centroid_vecs[train_labels[i]].append(h)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(train_prompts)}")
    centroids = {}
    for si in range(7):
        c = torch.stack(centroid_vecs[si]).mean(0)
        centroids[si] = c / c.norm()
    print(f"  7 centroids computed ({time.time()-t0:.1f}s)")

    # -- detect_concept_full: BYTE-IDENTICAL to v438 (full sorted (si,sim) vector) --
    def detect_concept_full(prompt):
        h = get_hidden_at_layer(model, tokenizer, prompt, DETECT_LAYER)
        h_norm = h / (h.norm() + 1e-8)
        sims = []
        for si, c in centroids.items():          # si order 0..6 preserved
            sims.append((si, cosine_sim(h_norm, c).item()))
        # stable sort by sim desc; ties keep ascending-si (matches v437 argmax: first/lowest si on tie)
        sims_sorted = sorted(sims, key=lambda x: -x[1])
        return sims_sorted

    print(f"\n[3] Detection + margin-gated QA (baseline / gated)...")
    results = []
    n_detect_ok = 0
    n_boost = 0          # (a) detect=Y & margin>=M & base-wrong & gated-correct
    n_blocked = 0        # (b) detect=N & margin<M  (gate fired on wrong detect)
    n_false_abstain = 0  # (c) detect=Y & margin<M  (gate suppressed a correct detect)
    for item in CLOZE_HELD:
        question = cloze_to_question(item["prompt"])

        sims_sorted = detect_concept_full(item["prompt"])
        top1_si, top1_sim = sims_sorted[0]
        top2_si, top2_sim = sims_sorted[1]
        margin = top1_sim - top2_sim
        detected_si = top1_si
        detect_ok = (detected_si == item["si"])
        n_detect_ok += int(detect_ok)

        gated = margin < M     # abstain: margin below threshold -> no retrieval (REP change vs v437 det_sim<TAU)

        ans_base = generate_answer(model, tokenizer, build_user_content(question, None))
        base_ok = answer_correct(item["si"], ans_base)

        if gated:
            ans_gated = ans_base      # no-retrieve: baseline answer, no extra generation
            retrieved = False
        else:
            ans_gated = generate_answer(model, tokenizer,
                                        build_user_content(question, GOLD_FRAGMENTS[detected_si]))
            retrieved = True
        gated_ok = answer_correct(item["si"], ans_gated)

        boost = detect_ok and (not gated) and (not base_ok) and gated_ok
        blocked = (not detect_ok) and gated
        false_abstain = detect_ok and gated
        n_boost += int(boost)
        n_blocked += int(blocked)
        n_false_abstain += int(false_abstain)

        r = {
            "id": item["id"], "true_si": item["si"], "question": question,
            "detected_si": detected_si, "detect_ok": detect_ok,
            "top1_si": top1_si, "top1_sim": round(top1_sim, 4),
            "top2_si": top2_si, "top2_sim": round(top2_sim, 4),
            "margin": round(margin, 4), "M": M, "gated": gated, "retrieved": retrieved,
            "base_ok": base_ok, "gated_ok": gated_ok,
            "boost": boost, "wrong_injection_blocked": blocked, "false_abstain": false_abstain,
            "ans_base": ans_base, "ans_gated": ans_gated,
        }
        results.append(r)

        d = "Y" if detect_ok else "N"
        g = "GATE" if gated else "pass"
        tag = "+boost" if boost else ("+block" if blocked else ("-fabst" if false_abstain else "      "))
        print(f"  {item['id']:4s}: detect={d} margin={margin:.4f} {g} | "
              f"base={'OK ' if base_ok else 'no '} gated={'OK ' if gated_ok else 'no '} [{tag}]")

    # -- margin separability (from run) --
    correct_margins = [r["margin"] for r in results if r["detect_ok"]]
    wrong_margins = [r["margin"] for r in results if not r["detect_ok"]]
    min_correct = min(correct_margins) if correct_margins else None
    max_wrong = max(wrong_margins) if wrong_margins else None
    gap = (min_correct - max_wrong) if (min_correct is not None and max_wrong is not None) else None

    n_wrong_detects = len(wrong_margins)
    n_wrong_passed = sum(1 for r in results if (not r["detect_ok"]) and (not r["gated"]))
    block_ok = (n_wrong_passed == 0)
    boost_ok = (n_boost >= PASS_BOOST)

    # explicit F2h transition (false-abstain@v437 -> boost@v439?)
    m = {r["id"]: r for r in results}
    f2h = m.get("F2h", {})
    f2h_state = ("boost" if f2h.get("boost") else
                 ("false_abstain" if f2h.get("false_abstain") else
                  ("blocked" if f2h.get("wrong_injection_blocked") else "neither")))
    f2h_recovered = bool(f2h.get("boost"))   # v437 false-abstained F2h; dominance requires it become boost

    if boost_ok and block_ok:
        verdict = "PASS"
        conclusion = (f"Margin-gate at M={M} DOMINATES v437 max-cosine gate on the 7 held-out: "
                      f"mechanistic boost {n_boost}/7 (>= {PASS_BOOST}) AND blocks both "
                      f"{n_wrong_detects} wrong-detect injections. F2h {f2h_state} "
                      f"(recovered={f2h_recovered}). Margin trigger is mechanically superior on this "
                      f"set (necessary, not sufficient -- N=7, m fit; OWED-GENERALIZATION v440+).")
    else:
        verdict = "FAIL"
        reasons = []
        if not boost_ok:
            reasons.append(f"boost {n_boost}/7 < {PASS_BOOST} (did NOT recover enough correct retrievals; "
                           f"F2h={f2h_state}, false-abstain={n_false_abstain}, margin gap={gap})")
        if not block_ok:
            reasons.append(f"{n_wrong_passed}/{n_wrong_detects} wrong-detect(s) passed the gate at M={M} "
                           f"(margin >= M on a wrong-concept -> wrong GOLD injected)")
        conclusion = ("Margin-gate does NOT dominate the v437 max-cosine gate: " + "; ".join(reasons) +
                      ". Margin geometric trigger yields no gain over max-cosine on this set. "
                      "Close the geometric-trigger line; pivot to a NON-geometric retrieval trigger "
                      "(retrieval-verification / abstain-by-agreement / answer-consistency).")

    print(f"\n{'='*72}")
    print(f"G3 VERDICT: {verdict}")
    print(f"  Detection (held-out):         {n_detect_ok}/7")
    print(f"  (a) mechanistic boost:        {n_boost}/7   (need {PASS_BOOST} = DOMINANCE)")
    print(f"  (b) wrong-injections blocked: {n_blocked}/{n_wrong_detects}")
    print(f"  (c) false-abstain:            {n_false_abstain}/{len(correct_margins)}")
    print(f"  F2h transition:               v437 false-abstain -> v439 {f2h_state}  (recovered={f2h_recovered})")
    print(f"  margin separability: min_correct={min_correct}  max_wrong={max_wrong}  gap={gap}")
    print(f"  wrong-detects passing gate:   {n_wrong_passed}/{n_wrong_detects}")
    print(f"  {conclusion}")
    print(f"{'='*72}")

    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v439", "axis": "retrieval-trigger-margin-gate", "track": "ORGANISM",
        "model": MODEL_ID, "detect_layer": DETECT_LAYER, "M": M,
        "method": "cosine-to-centroid @L13 detect (full sorted vector); gate margin(top1-top2)<M -> no-retrieve(baseline) else detected-GOLD; greedy gen; keyword correctness",
        "pass_boost": PASS_BOOST,
        "n_detect_ok": n_detect_ok, "n_boost": n_boost, "n_blocked": n_blocked,
        "n_false_abstain": n_false_abstain,
        "f2h_transition": {"v437": "false_abstain", "v439": f2h_state, "recovered": f2h_recovered},
        "separability": {"min_correct": min_correct, "max_wrong": max_wrong, "gap": gap,
                         "wrong_detects": n_wrong_detects, "wrong_passed_gate": n_wrong_passed},
        "results": results, "verdict": verdict, "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
