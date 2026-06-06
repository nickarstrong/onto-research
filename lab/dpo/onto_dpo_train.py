import json, argparse

def load_dpo_data(path, max_pairs=None):
    records = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            records.append({'prompt': row['prompt'], 'chosen': row['chosen'], 'rejected': row['rejected']})
    if max_pairs:
        records = records[:max_pairs]
    print(f'Loaded {len(records)} DPO pairs')
    return records

def compute_logprobs(model, tokenizer, prompt, response, device):
    text = prompt + ' ' + response
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=1024).to(device)
    prompt_ids = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=256)
    prompt_len = prompt_ids['input_ids'].shape[1]
    with __import__('torch').no_grad() if not model.training else __import__('contextlib').nullcontext():
        import torch
        outputs = model(**inputs)
        logits = outputs.logits[:, prompt_len-1:-1, :]
        target_ids = inputs['input_ids'][:, prompt_len:]
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
        token_log_probs = log_probs.gather(2, target_ids.unsqueeze(2)).squeeze(2)
        return token_log_probs.sum()

def dpo_loss(policy_chosen_logps, policy_rejected_logps, ref_chosen_logps, ref_rejected_logps, beta=0.1):
    import torch
    chosen_rewards = beta * (policy_chosen_logps - ref_chosen_logps)
    rejected_rewards = beta * (policy_rejected_logps - ref_rejected_logps)
    loss = -torch.nn.functional.logsigmoid(chosen_rewards - rejected_rewards)
    return loss

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--output', default='onto-qwen-lora')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--lr', type=float, default=5e-6)
    parser.add_argument('--beta', type=float, default=0.1)
    parser.add_argument('--adapter', required=True, help='path to extracted adapter_E4 dir (DPO поверх C)')
    args = parser.parse_args()
    MODEL = 'Qwen/Qwen2.5-Coder-7B'  # base, как у SFT-C (НЕ -Instruct)

    print('=== STEP 1: Loading model (4-bit) ===')
    from datasets import Dataset
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0)}')

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map='auto', trust_remote_code=True, torch_dtype=torch.float16)
    model.config.use_cache = False
    print('Model loaded.')

    print('=== STEP 2: LoRA (поверх adapter_E4 = C) ===')
    from peft import PeftModel, prepare_model_for_kbit_training
    model = prepare_model_for_kbit_training(model)
    model = PeftModel.from_pretrained(model, args.adapter, is_trainable=True)  # старт = C; ref_logprobs ниже = C
    t = sum(p.numel() for p in model.parameters() if p.requires_grad)
    a = sum(p.numel() for p in model.parameters())
    print(f'Trainable: {t:,} / {a:,} ({100*t/a:.2f}%)')

    print('=== STEP 3: Reference logprobs ===')
    data = load_dpo_data(args.data, 10 if args.test else None)
    device = next(model.parameters()).device

    model.eval()
    ref_logprobs = []
    for i, pair in enumerate(data):
        c_lp = compute_logprobs(model, tokenizer, pair['prompt'], pair['chosen'], device).item()
        r_lp = compute_logprobs(model, tokenizer, pair['prompt'], pair['rejected'], device).item()
        ref_logprobs.append((c_lp, r_lp))
        if (i+1) % 50 == 0 or i == len(data)-1:
            print(f'  Ref logprobs: {i+1}/{len(data)}')
    print(f'Reference logprobs computed for {len(data)} pairs')

    print('=== STEP 4: DPO Training ===')
    model.train()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr)
    grad_accum = 8
    max_steps = 2 if args.test else None
    num_epochs = 1 if args.test else args.epochs

    global_step = 0
    for epoch in range(num_epochs):
        total_loss = 0
        optimizer.zero_grad()
        for i, pair in enumerate(data):
            ref_c, ref_r = ref_logprobs[i]
            policy_c = compute_logprobs(model, tokenizer, pair['prompt'], pair['chosen'], device)
            policy_r = compute_logprobs(model, tokenizer, pair['prompt'], pair['rejected'], device)
            loss = dpo_loss(policy_c, policy_r, ref_c, ref_r, args.beta) / grad_accum
            loss.backward()
            total_loss += loss.item() * grad_accum

            if (i + 1) % grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1
                avg = total_loss / (i + 1)
                print(f'  Epoch {epoch+1} Step {global_step} Loss: {loss.item()*grad_accum:.4f} Avg: {avg:.4f}')
                if max_steps and global_step >= max_steps:
                    break

        if (len(data)) % grad_accum != 0:
            optimizer.step()
            optimizer.zero_grad()

        avg_loss = total_loss / len(data)
        print(f'  Epoch {epoch+1} done. Avg loss: {avg_loss:.4f}')
        if max_steps and global_step >= max_steps:
            break

    print(f'=== STEP 5: Saving to {args.output}/ ===')
    import os
    os.makedirs(args.output, exist_ok=True)
    model.save_pretrained(args.output)
    tokenizer.save_pretrained(args.output)
    print('=== DONE ===')

if __name__ == '__main__':
    main()
