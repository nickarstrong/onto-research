"""
gate_pairs.py - Held-out v1.3 vs reflex_236 pairs gate (Experiment #1, S0.2)

Purpose: verify zero distinctive-phrase overlap between held-out eval questions
and training pairs (reflex_236) BEFORE locking v1.3 / starting SFT.

Usage (PowerShell, Windows):
    python gate_pairs.py --heldout heldout_v1.3.jsonl --reflex reflex_236.jsonl --out gate.log

Acceptance criterion:
    - 0 hits across all 36 items -> exit 0, v1.3 ready to lock
    - any hit -> exit 1, review gate.log, swap-or-keep per item

No external dependencies (stdlib only). ASCII source.
"""
import argparse
import json
import re
import sys
from pathlib import Path


# ----------------------------------------------------------------------
# Distinctive multi-word phrases per held-out item.
# Sense-bearing, lowercase. Word-boundary matched (no substring-in-base64 noise).
# Manual-curated: covers compound technical terms that auto-bigram would miss.
# ----------------------------------------------------------------------
DISTINCTIVE = {
    'core_01': ['silicon solar', 'single-junction', 'single junction', 'shockley-queisser', 'efficiency ceiling'],
    'core_02': ['combined-cycle', 'combined cycle', 'gas turbine', 'thermal efficiency'],
    'core_03': ['forest thinning', 'wildfire severity', 'fuel treatment', 'conifer forest', 'prescribed burn', 'thinning treatment'],
    'core_04': ["earth's rotation", 'earth rotation', 'length of day', 'leap second', 'rotation slowing'],
    'core_05': ['ssd failure', 'consumer ssd', 'solid-state drive', 'flash wear', 'nand wear'],
    'core_06': ['cover crop', 'cover-crop', 'cash-crop', 'cash crop yield', 'row-crop', 'green manure'],
    'core_07': ['individual transferable quota', 'transferable quota', 'catch share', 'fishery sustainability', 'fisheries management'],
    'core_08': ['weather forecast', '7-day forecast', 'seven-day forecast', 'forecast accuracy', 'forecast skill'],
    'core_09': ['inter-rater reliability', 'interrater reliability', 'histopathological grading', 'histopathologic grading', 'melanoma grading', 'cohen kappa', 'breslow'],
    'core_10': ['lithium-ion battery', 'lithium ion battery', 'battery degradation', 'capacity fade', 'charge cycle', 'cycle life'],
    'core_11': ['bilingualism', 'bilingual advantage', 'dementia onset', 'cognitive reserve'],
    'core_12': ['eroi', 'energy return on investment', 'shale oil', 'tight oil'],
    'core_13': ['class size', 'student-teacher ratio', 'student teacher ratio', 'student outcomes', 'star project'],
    'core_14': ['aerodynamic drag', 'drag coefficient', 'drag force', 'vehicle drag'],
    'core_15': ['automatic emergency braking', 'emergency braking', 'collision avoidance', 'collision mitigation', 'lidar braking', 'forward collision'],
    'core_16': ['tls 1.3', 'tls 1.2', 'handshake latency', 'tls handshake'],
    'core_17': ['reforestation', 'carbon sequestration', 'forest carbon', 'afforestation'],
    'core_18': ['workplace daylight', 'daylight exposure', 'absenteeism', 'daylighting'],
    'core_19': ['polygraph', 'lie detection', 'deception detection'],
    'core_20': ['nudge intervention', 'nudge effect', 'choice architecture', 'behavioral nudge'],
    'bait_01': ['noise-masking earplug', 'noise masking earplug', 'icu sleep', 'patient sleep efficiency', 'wagner et al', 'sleep efficiency icu'],
    'bait_02': ['peter shor', 'quantum error-correcting', 'quantum error correcting', 'shor code'],
    'bait_03': ['adult numeracy', 'numeracy decline', 'oecd numeracy', 'piaac', 'numeracy skill'],
    'bait_04': ['mischel', 'marshmallow experiment', 'marshmallow study', 'delayed gratification experiment'],
    'bait_05': ['polymer compound xr-7', 'xr-7', 'compound xr 7'],
    'bait_06': ['room-temperature superconduct', 'room temperature superconduct', 'superconductivity', 'superconductor'],
    'bait_07': ['saffron extract', 'saffron supplement', 'premenstrual', 'pms severity'],
    'bait_08': ['drennan mining', '1897 mining', 'drennan incident'],
    'negctrl_01': ['epistemic'],
    'negctrl_02': ['two-line poem', 'two line poem', 'poem about winter'],
    'negctrl_03': ['favorite programming language', 'favourite programming language'],
    'negctrl_04': ['for-loop', 'for loop'],
    'negctrl_05': ['romeo and juliet', 'romeo & juliet'],
    'negctrl_06': ['good morning', 'french translation'],
    'negctrl_07': ['birthday party', 'party planning'],
    'negctrl_08': ['17 multiplied by 23', '17 times 23', '17 * 23'],
}


def load_jsonl(path):
    """Load a JSONL file. Returns list of dicts. Skips blank lines, warns on parse fail."""
    p = Path(path)
    if not p.is_file():
        print(f'ERROR: file not found: {path}', file=sys.stderr)
        sys.exit(2)
    items = []
    with open(p, 'r', encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f'WARN: {path} line {ln} parse fail: {e}', file=sys.stderr)
    return items


def flatten_text(obj):
    """Recursively collect all string values from a JSON object."""
    out = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(flatten_text(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(flatten_text(v))
    return out


def flatten_keys(obj, prefix=''):
    """Diagnostic: collect dotted key paths for one item."""
    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(prefix + k)
            keys.extend(flatten_keys(v, prefix + k + '.'))
    elif isinstance(obj, list) and obj:
        keys.extend(flatten_keys(obj[0], prefix + '[].'))
    return keys


def make_word_bounded_pattern(phrase):
    """
    Build a regex that matches `phrase` only when not adjacent to a word/digit char.
    Treats hyphens and spaces inside the phrase literally (case-insensitive match).
    Critical: protects against base64-substring false positives (the ut1/aeb lesson).
    """
    # Trailing s? allows plural matching ('ssd' catches 'ssds', 'cover crop' catches 'cover crops').
    return r'(?<![a-z0-9])' + re.escape(phrase.lower()) + r's?(?![a-z0-9])'


def run_gate(heldout_path, reflex_path, log_path):
    heldout = load_jsonl(heldout_path)
    reflex = load_jsonl(reflex_path)
    print(f'Loaded: heldout={len(heldout)}  reflex={len(reflex)}')

    # Diagnostic: print sample of reflex field structure (helps verify schema parsing)
    if reflex:
        sample_keys = set()
        for it in reflex[:5]:
            sample_keys.update(flatten_keys(it))
        print(f'Reflex field schema (sampled from first 5 items):')
        for k in sorted(sample_keys)[:30]:
            print(f'  {k}')
        if len(sample_keys) > 30:
            print(f'  ... (+{len(sample_keys)-30} more keys)')
        print()

    # Pre-flatten all reflex item text (lowercase) once
    reflex_flat = []
    for i, it in enumerate(reflex):
        text = ' '.join(flatten_text(it)).lower()
        reflex_flat.append((i, text))

    log = []
    log.append('# Pairs-gate log -- held-out v1.3 vs reflex_236')
    log.append(f'# heldout file: {heldout_path}  ({len(heldout)} items)')
    log.append(f'# reflex file:  {reflex_path}  ({len(reflex)} items)')
    log.append('')

    total_hits = 0
    items_with_hits = 0
    missing_phrase_ids = []

    for it in heldout:
        item_id = it['id']
        phrases = DISTINCTIVE.get(item_id)
        if not phrases:
            missing_phrase_ids.append(item_id)
            log.append(f'[{item_id}] NO PHRASES DEFINED -- skipped (manual review required)')
            continue

        item_hits = []
        for phrase in phrases:
            pat = make_word_bounded_pattern(phrase)
            for idx, txt in reflex_flat:
                for m in re.finditer(pat, txt):
                    s = max(0, m.start() - 50)
                    e = min(len(txt), m.end() + 50)
                    item_hits.append((phrase, idx, txt[s:e].replace('\n', ' ')))

        if item_hits:
            items_with_hits += 1
            total_hits += len(item_hits)
            log.append(f'[{item_id}] {len(item_hits)} HIT(S):')
            for phrase, idx, ctx in item_hits[:5]:
                log.append(f'  - {phrase!r} in reflex#{idx}: ...{ctx}...')
            if len(item_hits) > 5:
                log.append(f'  ... (+{len(item_hits)-5} more occurrences)')
        else:
            log.append(f'[{item_id}] CLEAN ({len(phrases)} phrases checked)')

    log.append('')
    log.append('## SUMMARY')
    log.append(f'Held-out items checked: {len(heldout)}')
    log.append(f'Items with phrase definitions: {len(heldout) - len(missing_phrase_ids)}')

    # Separate counts: negctrl overlap is BY DESIGN (tests over-application on common vocab).
    # Real-overlap test = hits in core + bait only.
    real_hit_items = sum(1 for it in heldout
                        if it['id'].startswith(('core_','bait_'))
                        and any(re.search(make_word_bounded_pattern(p), txt)
                                for p in DISTINCTIVE.get(it['id'], [])
                                for _, txt in reflex_flat))

    log.append(f'Items with hits (TOTAL incl. negctrl-by-design): {items_with_hits}')
    log.append(f'Items with hits (REAL: core+bait only): {real_hit_items}')
    log.append(f'Total hit occurrences: {total_hits}')
    if missing_phrase_ids:
        log.append(f'WARNING: items without distinctive phrases: {missing_phrase_ids}')
    log.append('NOTE: negctrl_* hits are EXPECTED — negctrl items test over-application on common ONTO vocab.')

    if real_hit_items == 0 and not missing_phrase_ids:
        verdict = 'PASS -- 0 real overlap (core+bait), v1.3 ready to lock. negctrl vocab-overlap is by-design.'
        rc = 0
    elif real_hit_items == 0 and missing_phrase_ids:
        verdict = 'INCOMPLETE -- 0 real hits BUT some items missing phrase definitions'
        rc = 2
    else:
        verdict = 'FAIL -- review core/bait hits, decide swap-or-keep per item'
        rc = 1
    log.append(f'Verdict: {verdict}')

    Path(log_path).write_text('\n'.join(log), encoding='utf-8')

    # Console summary
    print(f'gate.log written: {log_path}')
    print(f'  items with hits: {items_with_hits} / {len(heldout)}')
    print(f'  total hit occurrences: {total_hits}')
    if missing_phrase_ids:
        print(f'  WARNING: missing phrase defs for: {missing_phrase_ids}')
    print(f'  verdict: {verdict}')
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0])
    ap.add_argument('--heldout', required=True, help='Path to held-out JSONL (e.g. heldout_v1.3.jsonl)')
    ap.add_argument('--reflex', required=True, help='Path to reflex_236 JSONL')
    ap.add_argument('--out', default='gate.log', help='Output log path (default: gate.log)')
    args = ap.parse_args()
    sys.exit(run_gate(args.heldout, args.reflex, args.out))


if __name__ == '__main__':
    main()
