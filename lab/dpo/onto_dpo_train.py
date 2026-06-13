import json, argparse

# onto_dpo_train.py
# v2 (2026-06-14, fix(b) step3): adapted for bounded DPO LoRA on the FROZEN base.
#   - --adapter is now OPTIONAL. Absent  -> fix(b): a FRESH LoRA on the bare frozen base
#                                            (SPEC_fixb_dpo_gate.md sec2 ceilings, enforced below).
#                                Present -> legacy E-leg: continue an existing adapter (unchanged path).
#   - prompt format = format_example imported from run_ordinary_window.py (byte-exact inference wrapper;
#     md5 8b6366b1). No hand-typed wrapper -> train/gate format cannot drift.
#   - reference logprobs computed with the adapter DISABLED -> reference == frozen base (clean DPO ref).
#   - defaults moved to SPEC sec2 (epochs 1, beta 0.3, lr 5e-6). No merge: save_pretrained = adapter only.
#   - fix(b) mode asserts the SPEC sec2 ceilings; the script refuses to exceed them (R7 defense-in-depth).

# byte-exact inference wrapper, reused (NOT re-typed) from the frozen harness
from run_ordinary_window import format_example   # f"### Instruction:\n{q}\n\n### Response:\n"

MAXLEN_FULL = 1536   # covers the longest chosen (~3.5k chars / echo-loop degenerates) without truncating the declare tail
MAXLEN_PROMPT = 256  # prompts are <130 chars; ample


def load_dpo_data(path, max_pairs=None):
    records = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            records.append({'prompt': row['prompt'], 'chosen': row['chosen'], 'rejected': row['rejected']})
    if max_pairs:
        records = records[:max_pairs]
    print(f'Loaded {len(records)} DPO pairs')
    return records


def compute_logprobs(model, tokenizer, prompt, response, device):
    import torch, contextlib
    wrapped = format_example(prompt)                 # exact inference context
    text = wrapped + response
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=MAXLEN_FULL).to(device)
    prompt_ids = tokenizer(wrapped, return_tensors='pt', truncation=True, max_length=MAXLEN_PROMPT)
    prompt_len = prompt_ids['input_ids'].shape[1]
    ctx = torch.no_grad() if not model.training else contextlib.nullcontext()
    with ctx:
        outputs = model(**inputs)
        logits = outputs.logits[:, prompt_len - 1:-1, :]
        target_ids = inputs['input_ids'][:, prompt_len:]
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
        token_log_probs = log_probs.gather(2, target_ids.unsqueeze(2)).squeeze(2)
        return token_log_probs.sum()


def dpo_loss(policy_chosen_logps, policy_rejected_logps, ref_chosen_logps, ref_rejected_logps, beta):
    import torch
    chosen_rewards = beta * (policy_chosen_logps - ref_chosen_logps)
    rejected_rewards = beta * (policy_rejected_logps - ref_rejected_logps)
    loss = -torch.nn.functional.logsigmoid(chosen_rewards - rejected_rewards)
    return loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--output', default='adapter_fixb_dpo_v1')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--epochs', type=int, default=1)      # SPEC sec2: 1 epoch
    parser.add_argument('--lr', type=float, default=5e-6)     # SPEC sec2: LR <= 5e-6
    parser.add_argument('--beta', type=float, default=0.3)    # SPEC sec2: beta >= 0.3
    parser.add_argument('--grad-accum', type=int, default=8)
    parser.add_argument('--lora-r', type=int, default=8)          # SPEC sec2: r <= 8
    parser.add_argument('--lora-alpha', type=int, default=16)     # SPEC sec2: alpha <= 16
    parser.add_argument('--lora-dropout', type=float, default=0.05)
    parser.add_argument('--adapter', default=None,
                        help='OPTIONAL. If set: continue this adapter (legacy E-leg). '
                             'If unset: fresh LoRA on the bare frozen base (fix(b)).')
    args = parser.parse_args()
    MODEL = 'Qwen/Qwen2.5-Coder-7B'  # base, identical to e5_gen arm A / run_ordinary_window
    FIXB = args.adapter is None

    if FIXB:
        # SPEC_fixb_dpo_gate.md sec2 FROZEN ceilings -- the script refuses to exceed them (R7).
        assert args.lora_r <= 8,        f'STOP: lora_r {args.lora_r} > 8 (SPEC sec2 ceiling)'
        assert args.lora_alpha <= 16,   f'STOP: lora_alpha {args.lora_alpha} > 16 (SPEC sec2 ceiling)'
        assert args.lora_dropout == 0.05, f'STOP: lora_dropout {args.lora_dropout} != 0.05 (SPEC sec2)'
        assert args.beta >= 0.3,        f'STOP: beta {args.beta} < 0.3 (SPEC sec2 ceiling)'
        assert args.lr <= 5e-6,         f'STOP: lr {args.lr} > 5e-6 (SPEC sec2 ceiling)'
        assert args.epochs == 1,        f'STOP: epochs {args.epochs} != 1 (SPEC sec2)'

    print('=== STEP 1: Loading model (4-bit) ===')
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    assert torch.cuda.is_available(), 'STOP: CUDA not available -- DPO must run on GPU'
    print(f'CUDA: {torch.cuda.is_available()} | GPU: {torch.cuda.get_device_name(0)} | n_gpu: {torch.cuda.device_count()}')

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map='auto',
                                                 trust_remote_code=True, torch_dtype=torch.float16)
    model.config.use_cache = False
    print('Model loaded.')

    from peft import PeftModel, LoraConfig, get_peft_model, prepare_model_for_kbit_training
    model = prepare_model_for_kbit_training(model)
    if FIXB:
        print('=== STEP 2: FRESH LoRA on bare frozen base (fix(b)) ===')
        lcfg = LoraConfig(r=args.lora_r, lora_alpha=args.lora_alpha,
                          target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],  # attention projections only
                          lora_dropout=args.lora_dropout, bias='none', task_type='CAUSAL_LM')
        model = get_peft_model(model, lcfg)
    else:
        print(f'=== STEP 2: continue existing adapter {args.adapter} (legacy) ===')
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=True)
    t = sum(p.numel() for p in model.parameters() if p.requires_grad)
    a = sum(p.numel() for p in model.parameters())
    print(f'Trainable: {t:,} / {a:,} ({100*t/a:.4f}%)')

    print('=== STEP 3: Reference logprobs (adapter DISABLED -> frozen base) ===')
    data = load_dpo_data(args.data, 10 if args.test else None)
    device = next(model.parameters()).device
    model.eval()
    ref_logprobs = []
    for i, pair in enumerate(data):
        with model.disable_adapter():
            c_lp = compute_logprobs(model, tokenizer, pair['prompt'], pair['chosen'], device).item()
            r_lp = compute_logprobs(model, tokenizer, pair['prompt'], pair['rejected'], device).item()
        ref_logprobs.append((c_lp, r_lp))
        if (i + 1) % 10 == 0 or i == len(data) - 1:
            print(f'  Ref logprobs: {i+1}/{len(data)}')
    print(f'Reference logprobs computed for {len(data)} pairs')

    print('=== STEP 4: DPO Training ===')
    model.train()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr)
    grad_accum = args.grad_accum
    max_steps = 2 if args.test else None
    num_epochs = 1 if args.test else args.epochs

    global_step = 0
    for epoch in range(num_epochs):
        total_loss = 0.0
        optimizer.zero_grad()
        stepped_at_end = False
        for i, pair in enumerate(data):
            ref_c, ref_r = ref_logprobs[i]
            policy_c = compute_logprobs(model, tokenizer, pair['prompt'], pair['chosen'], device)
            policy_r = compute_logprobs(model, tokenizer, pair['prompt'], pair['rejected'], device)
            loss = dpo_loss(policy_c, policy_r, ref_c, ref_r, args.beta) / grad_accum
            loss.backward()
            total_loss += loss.item() * grad_accum

            if (i + 1) % grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(filter(lambda p: p.requires_grad, model.parameters()), 1.0)
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1
                avg = total_loss / (i + 1)
                print(f'  Epoch {epoch+1} Step {global_step} Loss: {loss.item()*grad_accum:.4f} Avg: {avg:.4f}')
                if max_steps and global_step >= max_steps:
                    break
        # flush a trailing partial accumulation (30 pairs % 8 != 0)
        if len(data) % grad_accum != 0 and not (max_steps and global_step >= max_steps):
            torch.nn.utils.clip_grad_norm_(filter(lambda p: p.requires_grad, model.parameters()), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            global_step += 1
            stepped_at_end = True
        avg_loss = total_loss / len(data)
        print(f'  Epoch {epoch+1} done. Avg loss: {avg_loss:.4f} | optimizer steps so far: {global_step}'
              f'{" (incl. trailing partial)" if stepped_at_end else ""}')
        if max_steps and global_step >= max_steps:
            break

    print(f'=== STEP 5: Saving adapter (NO merge) to {args.output}/ ===')
    import os
    os.makedirs(args.output, exist_ok=True)
    model.save_pretrained(args.output)          # PeftModel.save_pretrained = adapter weights only, base untouched
    tokenizer.save_pretrained(args.output)
    saved = sorted(os.listdir(args.output))
    print('Saved files:', saved)
    assert any(f.startswith('adapter_model') for f in saved), 'STOP: no adapter_model.* written'
    assert not any(f == 'pytorch_model.bin' or f.startswith('model-0000') for f in saved), \
        'STOP: a full model shard was written -- merge leaked, adapter must stay separate'
    print('=== DONE === adapter saved separate, base frozen (no merge).')


if __name__ == '__main__':
    main()
