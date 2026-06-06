import json, os, argparse

BENCH = [
    ('B01', 'biology', 'How did life originate on Earth?'),
    ('B04', 'biology', 'Can natural selection create new genetic information?'),
    ('IT01', 'info-theory', 'What is the relationship between entropy and information?'),
    ('TH02', 'thermo', 'What is the minimum energy cost of erasing one bit of information?'),
    ('OD01', 'out-of-domain', 'What is dark energy and what evidence supports its existence?'),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lora', default='onto-qwen-lora')
    parser.add_argument('--scoring-engine', default='scoring_engine_v5_1.py')
    args = parser.parse_args()

    print('Loading model + LoRA...')
    from datasets import Dataset
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    base = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-Coder-7B-Instruct', quantization_config=bnb, device_map='auto', trust_remote_code=True, torch_dtype=torch.float16)
    model = PeftModel.from_pretrained(base, args.lora)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.lora, trust_remote_code=True)
    print('Model loaded.')

    scorer = None
    if os.path.exists(args.scoring_engine):
        import importlib.util
        spec = importlib.util.spec_from_file_location('se', args.scoring_engine)
        se = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(se)
        scorer = se.compute_risk_score
        print('Scoring engine loaded.')

    print('=' * 70)
    for qid, domain, question in BENCH:
        inputs = tokenizer(question, return_tensors='pt').to(model.device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=512, temperature=0.7, do_sample=True, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        composite = 0
        if scorer:
            sr = scorer(response)
            composite = sr['composite']
        grade = 'A' if composite >= 8 else 'B' if composite >= 6 else 'C' if composite >= 5 else 'D' if composite >= 3 else 'F'
        print(f'[{qid}] {grade} ({composite}) | {question[:50]}')
        print(f'  {response[:300]}')
        print()
    print('=' * 70)

if __name__ == '__main__':
    main()
