#!/usr/bin/env python3
"""One-command replay of archived operator-collected responses (NOT new model inference)."""
from pathlib import Path
import json,sys
from grade_responses import audit_data,score_export,to_markdown,to_html
from verify_package import run as verify_integrity
from graders.scoring import GOLD,grade
ROOT=Path(__file__).resolve().parent

def main():
    if not verify_integrity():
        print('STOP: frozen source integrity check failed',file=sys.stderr)
        return 1
    audit_data()
    for tid,gold in GOLD.items():
        assert grade(tid,json.dumps(gold,ensure_ascii=False))['exact_pass'],tid
        assert not grade(tid,'{}')['exact_pass'],tid
    src=ROOT/'trials'/'operator_export_original_2026-11-07.json'
    export=json.loads(src.read_text(encoding='utf-8'))
    r=score_export(export)
    out=ROOT/'results'/'reproduced';out.mkdir(parents=True,exist_ok=True)
    (out/'scores.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'scores.md').write_text(to_markdown(r),encoding='utf-8')
    (out/'scores.html').write_text(to_html(r),encoding='utf-8')
    n=sum(bool(x['exact_pass']) for x in r['trial_results'])
    print(f'REPRODUCED: {n} exact passes / {len(r["trial_results"])} operator-recorded slots')
    print('STATUS:',r['status'])
    print('Mixed-system model identities are missing: no per-model success or pass^k claimed.')
    print('Reports:',out)
    return 0  # successful descriptive replay, not claim of a complete frontier experiment
if __name__=='__main__':raise SystemExit(main())
