import sys, importlib
import controller, daemon

cap = {}
def fake_live_adapters(*a, **k):
    cap.clear(); cap.update(k)
    raise SystemExit("SMOKE_SENTINEL")
controller.live_adapters = fake_live_adapters

def run(argv):
    cap.clear()
    sys.argv = ["daemon.py"] + argv
    try:
        daemon.main()
    except SystemExit as e:
        if str(e) != "SMOKE_SENTINEL":
            return ("NO-INTERCEPT", str(e))
    return ("OK", cap.get("hard_topics", "ABSENT"))

r_on  = run(["--live", "--hard-topics", "--n", "8", "--selflearn-trace", "smoke_x.jsonl"])
r_off = run(["--live", "--n", "8", "--selflearn-trace", "smoke_x.jsonl"])

print("ON :", r_on,  "(want ('OK', True))")
print("OFF:", r_off, "(want ('OK', False))")
ok = r_on == ("OK", True) and r_off == ("OK", False)
import os
print("trace_written:", os.path.exists("smoke_x.jsonl"), "(want False)")
print("RESULT:", "PASS" if (ok and not os.path.exists("smoke_x.jsonl")) else "FAIL")
