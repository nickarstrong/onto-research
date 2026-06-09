import pyarrow  # preload first: dodge torch+transformers pyarrow SEH on this box
import json
import gold_retrieve as gr, verify_E16 as v
store = gr.GoldStore("eval/_local/gold_fixture_E18.json")
v._eval_heldout("eval/_local/heldout_E17.jsonl", store)
