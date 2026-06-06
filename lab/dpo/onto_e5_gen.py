# ONTO E5 — arm inference -> outputs_E5.json (+ leak gate on arm C)
# Decoding/prompt format VERBATIM from onto_exp1_e4_sft.py (E4) for comparability:
#   greedy (do_sample=False), max_new_tokens=512, same instruction wrapper, same GOLD prompt.
# Arms: A base | B base+GOLD | C base+adapter_E5 | D base+adapter_E5+GOLD. 68 questions (36 heldout + 32 bait).
# Run: python onto_e5_gen.py --adapter ./adapter_E5_dpo_61
import json, re, gc, argparse
from pathlib import Path
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument('--adapter', default='./adapter_E5_dpo_61')
args = parser.parse_args()

BASE_MODEL = 'Qwen/Qwen2.5-Coder-7B'   # base, как у C
MAX_LEN = 1024
GEN_MAX_NEW = 512
SUPPRESS_STRINGS = ["<|file_sep|>", "\u59d4\u7ec4\u7ec7\u90e8"]
LEAK_EXACT_MIN_WORDS = 10
LEAK_NGRAM_N = 7
LEAK_NGRAM_THRESH = 0.15
OUTPUTS_JSON = Path('outputs_E5.json')
LEAK_REPORT = Path('leak_report_E5.md')

held_rows = [json.loads(l) for l in open('heldout_v1.3.jsonl', encoding='utf-8')]
bait_rows = [json.loads(l) for l in open('bait_v2_n32.jsonl', encoding='utf-8')]
assert len(held_rows) == 36 and len(bait_rows) == 32, 'STOP: eval sets wrong size'
questions = [(r['id'], r['question']) for r in held_rows] + [(r['id'], r['question']) for r in bait_rows]
print('inference questions:', len(questions))

# leak corpus = SFT train outputs (323) + DPO chosen texts (61)
sft_rows = [json.loads(l) for l in open('sft_reflex_323.jsonl', encoding='utf-8')]
dpo_rows = [json.loads(l) for l in open('dpo_pairs_E5_v1.jsonl', encoding='utf-8')]
train_texts = [r['output'] for r in sft_rows] + [r['chosen'] for r in dpo_rows]
print('leak corpus texts:', len(train_texts))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0)}')

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def format_example(instruction):
    return f"### Instruction:\n{instruction}\n\n### Response:\n"

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                         bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=bnb,
                                            device_map='auto', trust_remote_code=True, torch_dtype=torch.float16)
model = PeftModel.from_pretrained(base, args.adapter)   # inference-only
model.eval()
print('Model + adapter_E5 loaded.')

def build_bad_words_ids():
    bad, seen, out = [], set(), []
    for s in SUPPRESS_STRINGS:
        for variant in (s, ' ' + s):
            ids = tokenizer(variant, add_special_tokens=False)['input_ids']
            if ids: bad.append(ids)
    for ids in bad:
        k = tuple(ids)
        if k not in seen: seen.add(k); out.append(ids)
    return out
BAD_WORDS_IDS = build_bad_words_ids()

GOLD_KERNEL_PROMPT = (
    "You operate under the ONTO R1-R18 epistemic protocol. Apply on every answer:\n"
    "R1 QUANTIFY: numbers not words. R2 UNCERTAINTY: state it explicitly. "
    "R3 COUNTERARGUMENTS: steel-man the strongest opposing view. R4 SOURCES: cite or disclaim; no source -> say so. "
    "R5 EVIDENCE GRADE: I (RCT/proof) > II (observational) > III (opinion). R6 FALSIFIABILITY: state what would disprove the claim. "
    "R7 NO FABRICATION: never invent citations, statistics, or DOIs (immutable). "
    "R8 if unknown: bound it and reason, do not halt and do not fabricate. R13 address the underlying need. "
    "R17 cross-check consistency. R18 remove filler; keep only sourced claims, real numbers, and honest uncertainty.\n"
)

def generate(model_obj, question, system_prompt=None):
    text = (system_prompt + '\n' if system_prompt else '') + format_example(question)
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=MAX_LEN).to(model_obj.device)
    gen_kwargs = dict(max_new_tokens=GEN_MAX_NEW, do_sample=False, num_beams=1,
                      bad_words_ids=BAD_WORDS_IDS, pad_token_id=tokenizer.pad_token_id,
                      eos_token_id=tokenizer.eos_token_id)
    with torch.no_grad():
        out = model_obj.generate(**inputs, **gen_kwargs)
    txt = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    for s in SUPPRESS_STRINGS:
        txt = txt.replace(s, '')
    return txt.strip()

def run_arm(model_obj, system_prompt, tag):
    res = []
    for i, (qid, q) in enumerate(questions, 1):
        res.append({'id': qid, 'output': generate(model_obj, q, system_prompt)})
        if i % 6 == 0: print(f'  [{tag}] {i}/{len(questions)}')
    torch.cuda.empty_cache(); gc.collect()
    return res

outputs = {}
def checkpoint_outputs(done_tag):
    order = [k for k in ['A','B','C','D'] if k in outputs]
    json.dump({k: outputs[k] for k in order}, open(OUTPUTS_JSON, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print(f'  [checkpoint] outputs_E5.json arms {order} (finished {done_tag})')

print('ARM C (adapter_E5, no prompt)')
outputs['C'] = run_arm(model, None, 'C'); checkpoint_outputs('C')
print('ARM D (adapter_E5 + GOLD prompt)')
outputs['D'] = run_arm(model, GOLD_KERNEL_PROMPT, 'D'); checkpoint_outputs('D')
with model.disable_adapter():
    print('ARM A (base, no prompt)')
    outputs['A'] = run_arm(model, None, 'A'); checkpoint_outputs('A')
    print('ARM B (base + GOLD prompt)')
    outputs['B'] = run_arm(model, GOLD_KERNEL_PROMPT, 'B'); checkpoint_outputs('B')

ordered = {k: outputs[k] for k in ['A','B','C','D'] if k in outputs}
json.dump(ordered, open(OUTPUTS_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Wrote', OUTPUTS_JSON, '| arms:', list(ordered.keys()))

# ---- leak gate on arm C (same detectors as E4) ----
WORD_RE = re.compile(r'\w+', re.UNICODE)
def words(t): return WORD_RE.findall(t.lower())
def ngrams(tok, n): return set(tuple(tok[i:i+n]) for i in range(len(tok)-n+1)) if len(tok) >= n else set()

train_word_seqs = [words(t) for t in train_texts]
pool = set()
for s in train_word_seqs: pool |= ngrams(s, LEAK_NGRAM_N)
phrases = set()
for s in train_word_seqs:
    for i in range(0, max(0, len(s)-LEAK_EXACT_MIN_WORDS+1)):
        phrases.add(' '.join(s[i:i+LEAK_EXACT_MIN_WORDS]))

lines = ['# Leak Report E5 — Arm C vs Train (sft_reflex_323 + dpo_chosen_61)\n']
any_leak = False
for item in outputs['C']:
    seq = words(item['output'])
    cphr = set(' '.join(seq[i:i+LEAK_EXACT_MIN_WORDS]) for i in range(0, max(0, len(seq)-LEAK_EXACT_MIN_WORDS+1)))
    hits = sorted(cphr & phrases)
    cng = ngrams(seq, LEAK_NGRAM_N)
    ov = len(cng & pool)/len(cng) if cng else 0.0
    leaked = bool(hits) or ov > LEAK_NGRAM_THRESH
    any_leak = any_leak or leaked
    lines.append(f"## {item['id']} — {'LEAK' if leaked else 'ok'}")
    lines.append(f'- 7-gram overlap: {ov:.3f}')
    for h in hits[:3]: lines.append(f'    - "{h}"')
    lines.append('')
lines.insert(1, f"**VERDICT: {'LEAK DETECTED' if any_leak else 'NO LEAK'}**\n")
LEAK_REPORT.write_text('\n'.join(lines), encoding='utf-8')
print('Wrote', LEAK_REPORT, '| any_leak =', any_leak)
print('=== GEN DONE === download outputs_E5.json + leak_report_E5.md')
