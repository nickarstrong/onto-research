import json, sys, datetime
import verify_E16_L4 as mod

CORPUS = "eval/_local/gold_corpus_live.json"
SMOKE  = "eval/_local/smoke_E16.jsonl"
REPORT = "reports/report_E16_smoke.md"
KEYS   = ("n_con","n_ent","S_size","pre_demoted")

def main():
    bind  = mod.L4Bind(CORPUS)
    items = [json.loads(l) for l in open(SMOKE, encoding="utf-8") if l.strip()]
    rows  = []
    for it in items:
        lab, rec = mod.verify_item(it, bind)
        rows.append({
            "id": it["id"], "cls": it.get("class",""), "exp": it["expect"],
            "got": lab, "l3": rec is not None, "ok": lab == it["expect"],
            "rec": (None if rec is None else {k: rec.get(k) for k in KEYS}),
        })
    n_con_ok = sum(1 for r in rows if r["exp"]=="CONTRADICTED" and r["got"]=="CONTRADICTED")
    n_cln_ok = sum(1 for r in rows if r["exp"]=="VERIFIED"     and r["got"]=="VERIFIED")
    all_l3   = all(r["l3"] for r in rows)
    all_ok   = all(r["ok"] for r in rows)
    verdict  = "PASS" if (n_con_ok>=1 and n_cln_ok>=1 and all_l3 and all_ok) else "FAIL"
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    L = []
    L.append("# report_E16_smoke -- E16 live-bind behavioural smoke")
    L.append("")
    L.append("date   : " + ts)
    L.append("corpus : gold_corpus_live.json (34 files / 366 recs, G2 GREEN; LOCAL, GOLD-derived)")
    L.append("organ  : verify_E16_L4 FROZEN md5 544c9a7b8c3189943b010a642efc0d86 (import-only)")
    L.append("model  : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (contradiction_idx=2)")
    L.append("")
    L.append("## per-item (no claim text; GOLD-derived stays local)")
    L.append("")
    L.append("| id | class | expect | got | L3 | n_con | n_ent | S | pre_demoted | pass |")
    L.append("|----|-------|--------|-----|----|-------|-------|---|-------------|------|")
    for r in rows:
        rc = r["rec"] or {}
        L.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            r["id"], r["cls"], r["exp"], r["got"], "yes" if r["l3"] else "NO",
            rc.get("n_con","-"), rc.get("n_ent","-"), rc.get("S_size","-"),
            rc.get("pre_demoted","-"), "PASS" if r["ok"] else "FAIL"))
    L.append("")
    L.append("## gate")
    L.append("- contra->CONTRADICTED : {} (need >=1)".format(n_con_ok))
    L.append("- clean ->VERIFIED     : {} (need >=1)".format(n_cln_ok))
    L.append("- all reach L3         : {}".format(all_l3))
    L.append("- all item asserts     : {}".format(all_ok))
    L.append("")
    L.append("VERDICT : " + verdict)
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    for r in rows:
        print(r["id"], r["exp"], "->", r["got"], "| L3", r["l3"], "| rec", r["rec"], "|", "PASS" if r["ok"] else "FAIL")
    print("\ncontra_ok={} clean_ok={} all_l3={} all_pass={}".format(n_con_ok, n_cln_ok, all_l3, all_ok))
    print("VERDICT:", verdict, "| report ->", REPORT)
    sys.exit(0 if verdict=="PASS" else 1)

if __name__ == "__main__":
    main()
