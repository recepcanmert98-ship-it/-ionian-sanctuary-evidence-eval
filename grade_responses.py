#!/usr/bin/env python3
"""Score original, human-collected frontier-chat responses with no API key.

Usage:
  py -3 grade_responses.py --self-test
  py -3 grade_responses.py --grade exported_frontier_trials.json
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
from statistics import mean
import sys
from graders.scoring import GOLD, ROOT, TASK_DIR, grade

DEFAULT_TRIALS = 3
TASK_IDS = sorted(GOLD)


def prompt_sha256(task_id: str) -> str:
    task = json.loads((TASK_DIR / f'{task_id}.json').read_text(encoding='utf-8'))
    return hashlib.sha256(task['prompt'].encode('utf-8')).hexdigest()


def audit_data() -> None:
    for task_id in TASK_IDS:
        task = json.loads((TASK_DIR / f'{task_id}.json').read_text(encoding='utf-8'))
        expected = GOLD[task_id]
        assert task['id'] == task_id
        assert set(task['output_schema']) == set(expected), f'{task_id} schema differs from reference'
        assert task['critical_fields'] and set(task['critical_fields']) <= set(expected)
        assert task['prompt'].strip() and task['source_ids']
    assert len(TASK_IDS) == 8, 'Unexpected number of archived tasks'


def score_export(export: dict) -> dict:
    if not isinstance(export, dict):
        raise ValueError('Export must be a JSON object')
    rows = export.get('trials')
    if not isinstance(rows, list):
        raise ValueError('Export needs a trials array')
    count = export.get('trials_per_task', DEFAULT_TRIALS)
    if type(count) is not int or not 1 <= count <= 5:
        raise ValueError('trials_per_task must be an integer 1–5')
    required = {(t, i) for t in TASK_IDS for i in range(1, count + 1)}
    seen = set()
    graded = []
    rejected = []
    for n, row in enumerate(rows):
        if not isinstance(row, dict):
            rejected.append({'row': n, 'reason': 'trial is not an object'}); continue
        task_id = row.get('task_id')
        trial = row.get('trial')
        if task_id not in GOLD:
            rejected.append({'row': n, 'reason': 'unknown task'}); continue
        if type(trial) is not int or not (1 <= trial <= count):
            rejected.append({'row': n, 'reason': 'trial must be an integer within declared range'}); continue
        pair = (task_id, trial)
        if pair in seen:
            rejected.append({'row': n, 'reason': 'duplicate task/trial'}); continue
        if row.get('prompt_sha256') != prompt_sha256(task_id):
            rejected.append({'row': n, 'reason': 'prompt hash does not match frozen packet'}); continue
        raw = row.get('raw_response')
        if not isinstance(raw, str) or not raw.strip():
            rejected.append({'row': n, 'reason': 'empty or missing original response'}); continue
        seen.add(pair)
        score = grade(task_id, raw)
        score.update(trial=trial,
                     raw_response=raw,
                     share_link=row.get('share_link', ''),
                     collected_at=row.get('collected_at', ''),
                     source='original response supplied by operator (not API-authenticated)')
        graded.append(score)
    missing = sorted(required - seen)
    # Never pool trials with different media protocols as a single comparable batch.
    invalid_media = [i for i,row in enumerate(rows) if isinstance(row,dict) and type(row.get('photographs_supplied', False)) is not bool]
    for i in invalid_media:
        rejected.append({'row': i, 'reason': 'photographs_supplied must be a boolean'})
    modes = {row.get('photographs_supplied', False) for row in rows if isinstance(row, dict) and type(row.get('photographs_supplied', False)) is bool}
    mixed_media = len(modes) > 1
    if mixed_media:
        rejected.append({'row': None, 'reason': 'mixed photograph-supplied and text-only sessions; do not pool modes'})
    system_id = str(export.get('model_reported', '')).strip()
    if not system_id or system_id.lower() in {'unreported', 'unspecified', 'unknown'}:
        rejected.append({'row': None, 'reason': 'exact tested system/version must be reported for a complete run'})
    complete = not missing and not rejected and len(graded) == len(required)

    task_results = []
    for task_id in TASK_IDS:
        items = sorted((s for s in graded if s['task_id'] == task_id), key=lambda s: s['trial'])
        task_results.append({
            'task_id': task_id,
            'observed_trials': len(items),
            'exact_passes': sum(s['exact_pass'] for s in items),
            'pass_at_k': bool(any(s['exact_pass'] for s in items)) if len(items) == count else None,
            'pass_power_k': bool(all(s['exact_pass'] for s in items)) if len(items) == count else None,
            'critical_accuracy': round(mean(s['critical_accuracy'] for s in items), 4) if items else None,
        })
    out = {
        'benchmark': 'Ionian Sanctuary evidence assessment v1.3',
        'collection_method': 'manual_free_consumer_chat',
        'results_authenticated_by_provider': False,
        'synthetic_or_mock_model_trials': False,
        'model_reported': export.get('model_reported', 'unspecified'),
        'photographic_protocol': 'mixed_invalid' if mixed_media else 'photographs_supplied' if modes == {True} else 'text_only',
        'model_platform': export.get('model_platform', ''),
        'trial_settings_reported': export.get('trial_settings_reported', 'new chat for each attempt'),
        'trials_per_task': count,
        'status': 'COMPLETE_OPERATOR_REPORTED' if complete else 'INCOMPLETE_NOT_FOR_MODEL_COMPARISON',
        'total_required': len(required),
        'total_validly_collected': len(graded),
        'rejected': rejected,
        'missing': [{'task_id': t, 'trial': n} for t, n in missing],
        'exact_pass_rate': round(mean(s['exact_pass'] for s in graded), 6) if graded else None,
        'field_accuracy': round(mean(s['field_accuracy'] for s in graded), 6) if graded else None,
        'critical_accuracy': round(mean(s['critical_accuracy'] for s in graded), 6) if graded else None,
        'pass_at_k': round(mean(t['pass_at_k'] for t in task_results), 6) if complete else None,
        'pass_power_k': round(mean(t['pass_power_k'] for t in task_results), 6) if complete else None,
        'task_results': task_results,
        'trial_results': graded,
    }
    return out


def to_markdown(r: dict) -> str:
    p = lambda x: 'N/A' if x is None else f'{x:.1%}'
    lines = [
        '# ARCH-EVAL — Ionian Evidence Evaluation',
        '',
        f"**Status:** {r['status']}",
        f"**Tested system/version (required for independent verification):** {r['model_reported']}",
        f"**Photographic protocol:** {r['photographic_protocol']}",
        f"**Collection method:** {r['collection_method']} (NOT provider authenticated)",
        f"**Completed trials:** {r['total_validly_collected']} / {r['total_required']}",
        f"**Exact pass rate:** {p(r['exact_pass_rate'])}",
        f"**Field accuracy:** {p(r['field_accuracy'])}",
        f"**Critical archaeological decision accuracy:** {p(r['critical_accuracy'])}",
        f"**pass@{r['trials_per_task']}:** {p(r['pass_at_k'])}",
        f"**pass^{r['trials_per_task']}:** {p(r['pass_power_k'])}",
        '',
        '### By task',
        '| Task | Trials | Exact passes | Critical accuracy | pass@k | pass^k |',
        '|---|---:|---:|---:|:---:|:---:|',
    ]
    for t in r['task_results']:
        x = lambda v: '–' if v is None else ('Yes' if v else 'No')
        lines.append(f"| {t['task_id']} | {t['observed_trials']} | {t['exact_passes']} | {p(t['critical_accuracy'])} | {x(t['pass_at_k'])} | {x(t['pass_power_k'])} |")
    lines += ['', '### Detailed scoring and failure notes',
              'An incorrect decision below reflects the fixed reference answer; interpretation still requires human domain review.', '']
    for t in r['trial_results']:
        wrong = [k for k, val in t['fields'].items() if not val]
        lines.append(f"- **{t['task_id']} trial {t['trial']}** — {'PASS' if t['exact_pass'] else 'FAIL'}; wrong/missing fields: {', '.join(wrong) or 'none'}; extra fields: {', '.join(t['extra_fields']) or 'none'}; valid JSON: {t['valid_json']}")
    lines += ['', '### Research integrity notes',
              '- Tested-system identifiers are operator-supplied and should be checked against the linked original sessions; they are not provider-authenticated.',
              '- Response collection is manual and not authenticated; deterministic scoring is automated.',
              '- Mixed photographic protocols or incomplete trials invalidate a comparative headline.',
              '- Review original transcripts, confirm quotations and source interpretation, and document all assistance in provenance notes.',
              '']
    if r['missing'] or r['rejected']:
        lines.append(f"**Missing trial slots:** {len(r['missing'])}; **rejected records:** {len(r['rejected'])}.")
    return '\n'.join(lines) + '\n'


def to_html(r: dict) -> str:
    safe = lambda s: html.escape(str(s), quote=True)
    p = lambda v: '—' if v is None else f'{v:.1%}'
    rows = ''.join(f'<tr><td>{safe(t["task_id"])}</td><td>{t["observed_trials"]}</td><td>{t["exact_passes"]}</td><td>{p(t["critical_accuracy"])}</td><td>{"Yes" if t["pass_power_k"] else "No" if t["pass_power_k"] is not None else "—"}</td></tr>' for t in r['task_results'])
    details = ''.join(
        '<details><summary>' + safe(f'{s["task_id"]} · trial {s["trial"]} · {"PASS" if s["exact_pass"] else "FAIL"}') +
        '</summary><p>Incorrect fields: ' + safe(', '.join(k for k, ok in s['fields'].items() if not ok) or 'none') +
        '</p><h4>Original recorded response</h4><pre>' + safe(s['raw_response']) + '</pre></details>'
        for s in r['trial_results'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ionian ARCH-EVAL report</title><style>body{{font:16px system-ui;max-width:1000px;margin:auto;padding:28px;background:#0e1725;color:#e7edf8}}h1{{font-size:2rem}}.muted{{color:#bcc9dc}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px}}.card,details{{border:1px solid #42506a;border-radius:12px;padding:16px;margin:9px 0;background:#18263c}}.value{{font-size:2rem;font-weight:800}}table{{width:100%;border-collapse:collapse;margin:24px 0}}td,th{{text-align:left;border-bottom:1px solid #42506a;padding:10px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#111c30;padding:12px;border-radius:8px}}small{{color:#b9c7db}}</style><h1>Ionian Sanctuary — Evidence Assessment</h1><p class="muted">{safe(r['status'])} · {safe(r['photographic_protocol'])}</p><p><strong>Operator-submitted original responses; externally authenticated session logs not supplied.</strong> Identifiers are retained in the machine-readable report for reproducibility and are omitted from this presentation view.</p><div class="cards"><div class="card">Exact pass<div class="value">{p(r['exact_pass_rate'])}</div></div><div class="card">Critical decisions<div class="value">{p(r['critical_accuracy'])}</div></div><div class="card">pass^{r['trials_per_task']}<div class="value">{p(r['pass_power_k'])}</div></div><div class="card">Trials<div class="value">{r['total_validly_collected']} / {r['total_required']}</div></div></div><h2>Task results</h2><table><tr><th>Task</th><th>Trials</th><th>Passes</th><th>Critical accuracy</th><th>pass^k</th></tr>{rows}</table><h2>Full original responses</h2>{details}<p><small>Research integrity: expert validation and transcript review remain mandatory. This report does not independently authenticate the tested system or trial isolation.</small></p></html>'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--grade', type=Path, help='JSON export from FRONTIER_REAL_TEST.html')
    parser.add_argument('--self-test', action='store_true', help='Verify tasks, oracle and error controls')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'results')
    args = parser.parse_args(argv)
    if args.self_test:
        audit_data()
        for task_id, gold in GOLD.items():
            correct = json.dumps(gold, ensure_ascii=False)
            assert grade(task_id, correct)['exact_pass'], task_id
            assert not grade(task_id, '{}')['exact_pass'], task_id
        print('PASS: 8/8 reference outputs, 8/8 deliberately empty incorrect outputs; task schemas verified.')
        print('These are local software checks, not measured performance of a tested frontier system.')
        return 0
    if not args.grade:
        parser.error('Provide --grade <export.json> or --self-test')
    try:
        audit_data()
        content = json.loads(args.grade.read_text(encoding='utf-8-sig'))
        result = score_export(content)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        stem = dt.datetime.now(dt.timezone.utc).strftime('IONIAN_REAL_%Y%m%d_%H%M%S_UTC')
        for name, content in [(stem+'.json',json.dumps(result,ensure_ascii=False,indent=2)),(stem+'.md',to_markdown(result)),(stem+'.html',to_html(result))]:
            (args.output_dir/name).write_text(content,encoding='utf-8')
        print(f"Status: {result['status']} | {result['total_validly_collected']}/{result['total_required']} valid trials")
        print(f"Exact: {result['exact_pass_rate']:.1%}" if result['exact_pass_rate'] is not None else 'Exact: N/A')
        print(f'Reports saved to: {args.output_dir.resolve()}')
        return 0 if result['status'].startswith('COMPLETE') else 2
    except (OSError, json.JSONDecodeError, ValueError, AssertionError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
