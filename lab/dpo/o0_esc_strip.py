#!/usr/bin/env python3
# o0_esc_strip.py -- WATCH-G PRECONDITION (sealed spec sec 1a). Strip ANSI/terminal ESC sequences
# from the raw held-out `claim` field AT SOURCE, BEFORE the Layer-2 binding rule runs. Raw Ollama
# capture embeds CSI cursor-ops mid-token (e.g. "ground\x1b[6D\x1b[Kgroundbreaking") which corrupt
# subject/token extraction (the likely origin of the "On February" garbage subjects in v292).
#
# POLICY: CSI sequences (\x1b[ ... letter) and bare control bytes are removed to EMPTY (not space),
# so a mid-token cursor-op rejoins the token instead of splitting it. Newlines/tabs -> single space.
# Then whitespace is collapsed. This is STRICTER than clean_for_parse (which subs to space); the
# oracle still calls clean_for_parse downstream as defense-in-depth.
#
# VERIFY (pass/fail): output carries 0 ESC (0x1B) bytes across all rows, row count unchanged,
# every id preserved. Prints PASS/FAIL.
#
# Usage: python o0_esc_strip.py heldout_raw_20260625.jsonl heldout_clean_20260625.jsonl
# COMPUTE: pure stdlib, no network, no GPU -> LOCAL.

import json, re, sys

_CSI  = re.compile(r'\x1b\[[0-9;?]*[ -/]*[@-~]')   # ANSI CSI: ESC [ params interm final
_OSC  = re.compile(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)')  # OSC ... BEL/ST
_ESC2 = re.compile(r'\x1b[@-Z\\-_]')               # two-char ESC sequences
_CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def strip_claim(s):
    s = s or ""
    s = _OSC.sub("", s)
    s = _CSI.sub("", s)
    s = _ESC2.sub("", s)
    s = s.replace("\n", " ").replace("\t", " ")
    s = _CTRL.sub("", s)
    return re.sub(r'\s+', " ", s).strip()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "heldout_raw_20260625.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "heldout_clean_20260625.jsonl"
    rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    out = []
    esc_in = 0
    for r in rows:
        c = r.get("claim", "")
        if "\x1b" in (c or ""):
            esc_in += 1
        r2 = dict(r)
        r2["claim"] = strip_claim(c)
        out.append(r2)
    with open(dst, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    esc_out = sum(1 for r in out if "\x1b" in (r.get("claim") or ""))
    ids_in  = [r.get("id") for r in rows]
    ids_out = [r.get("id") for r in out]
    ok = (esc_out == 0) and (len(rows) == len(out)) and (ids_in == ids_out)
    print("rows in/out      : %d / %d" % (len(rows), len(out)))
    print("rows with ESC in : %d" % esc_in)
    print("ESC bytes remain : %d  (MUST be 0)" % esc_out)
    print("ids preserved    : %s" % (ids_in == ids_out))
    print("\n[esc_strip] %s -> %s" % ("PASS" if ok else "FAIL", dst))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
