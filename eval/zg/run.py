#!/usr/bin/env python3
"""Frozen-budget document retrieval eval; see EVAL-DESIGN.md."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = Path(__file__).resolve().parent
QUERIES = EVAL_DIR / 'queries.json'
RUNS = EVAL_DIR / 'runs'
ROUTES = {'hybrid': [], 'fts': ['--fts'], 'vector': ['--vector']}
EXCLUDES = ['!upstream/**', '!.idea/**', '!deep-news/assets/**', '!viewer/static/**', '!eval/**']
METRICS = ['hit_at_1', 'primary_at_5', 'recall_at_5', 'recall_at_10', 'mrr_at_10', 'ndcg_at_10']
HIT_RE = re.compile(r'^#(\d+)(?: \[[^\]\n]+\])? matchedBy=(\S+)(?: score=\S+)? (.+):\d+(?:-\d+)?$', re.MULTILINE)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def corpus_snapshot(root: Path = ROOT) -> dict:
    """All visible Markdown in the declared scope; no gold-dependent dedup."""
    files = {}
    for base, dirs, names in os.walk(root):
        rel = Path(base).relative_to(root)
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in {'upstream', 'eval', '__pycache__'}
                         and (rel / d).as_posix() not in {'deep-news/assets', 'viewer/static'}
                         and not (Path(base) / d).is_symlink())
        for name in sorted(names):
            p = Path(base) / name
            if name.endswith('.md') and not name.startswith('.') and not p.is_symlink():
                files[p.relative_to(root).as_posix()] = digest(p.read_bytes())
    groups = defaultdict(list)
    for path, sha in sorted(files.items()):
        # Only curated audience/format copies are interchangeable. Jenny vs archive is not.
        key = ('copy', sha) if path.split('/')[0] in {'by-audience', 'by-format'} else ('path', path)
        groups[key].append(path)
    canonical = {path: paths[0] for paths in groups.values() for path in paths}
    return {'files': files, 'canonical': canonical,
            'sha256': digest(json.dumps(files, ensure_ascii=False, sort_keys=True).encode())}


def validate_spec(spec: dict, corpus: dict) -> None:
    seen = set()
    for q in spec['queries']:
        if q['id'] in seen or not q['query'].strip():
            raise ValueError(f"duplicate id or empty query: {q['id']}")
        seen.add(q['id'])
        relevant = q['relevant']
        if (q['kind'] == 'distractor') != (not relevant):
            raise ValueError(f"only distractors may have no gold: {q['id']}")
        docs = set()
        for g in relevant:
            paths = g['paths']
            if not paths or len(paths) != len(set(paths)) or g['grade'] not in (1, 2):
                raise ValueError(f'invalid gold: {g}')
            if any(p not in corpus['files'] for p in paths):
                raise ValueError(f'missing/out-of-scope gold: {g}')
            keys = {corpus['canonical'][p] for p in paths}
            if len(keys) != 1 or docs.intersection(keys):
                raise ValueError(f'overlapping or nonidentical gold: {g}')
            docs.update(keys)
            aliases = {p for p, c in corpus['canonical'].items() if c in keys}
            if aliases != set(paths):
                raise ValueError(f'gold aliases changed; review paths: {g}')
        if relevant and not any(g['grade'] == 2 for g in relevant):
            raise ValueError(f"missing primary: {q['id']}")


def parse_hits(stdout: str) -> list[dict]:
    hits = [{'rank': int(m[1]), 'matched_by': m[2], 'path': m[3]}
            for m in HIT_RE.finditer(stdout)]
    counts = re.findall(r'^hits: (\d+)\s*$', stdout, re.MULTILINE)
    if len(counts) != 1 or int(counts[0]) != len(hits):
        raise ValueError('unrecognized/truncated zg output: hits count does not match headers')
    if [h['rank'] for h in hits] != list(range(1, len(hits) + 1)):
        raise ValueError('noncontiguous/duplicate/out-of-order zg ranks')
    return hits


def document_hits(hits: list[dict], corpus: dict) -> list[dict]:
    docs, seen = [], set()
    for h in hits:
        path = h['path']
        if path not in corpus['canonical']:
            raise ValueError(f'out-of-scope or nonexistent result (possible leakage): {path}')
        key = corpus['canonical'][path]
        if key not in seen:
            seen.add(key)
            docs.append({**h, 'raw_rank': h['rank'], 'rank': len(docs) + 1, 'document_id': key})
    return docs


def dcg(grades: list[int]) -> float:
    return sum((2 ** grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(grades, 1))


def metrics_for(hits: list[dict], relevant: list[dict], k: int = 10) -> dict:
    if k != 10:
        raise ValueError('fixed @5/@10 metrics require k=10')
    if not relevant:
        return {**dict.fromkeys(METRICS), 'first_relevant_rank': None}
    gold = {p: i for i, g in enumerate(relevant) for p in g['paths']}
    if len(gold) != sum(len(g['paths']) for g in relevant):
        raise ValueError('overlapping gold paths')
    covered, grades, primary = set(), [], False
    recall5 = 0
    for rank, hit in enumerate(hits[:10], 1):
        key = gold.get(hit['path'])
        grade = relevant[key]['grade'] if key is not None and key not in covered else 0
        if key is not None:
            covered.add(key)
        grades.append(grade)
        if rank <= 5:
            recall5 = len(covered)
            primary |= grade == 2
    first = next((i for i, grade in enumerate(grades, 1) if grade), None)
    return {'hit_at_1': float(bool(grades and grades[0])), 'primary_at_5': float(primary),
            'recall_at_5': recall5 / len(relevant), 'recall_at_10': len(covered) / len(relevant),
            'mrr_at_10': 1 / first if first else 0.,
            'ndcg_at_10': dcg(grades) / dcg(sorted([g['grade'] for g in relevant], reverse=True)[:10]),
            'first_relevant_rank': first}


def run_zg(query: str, route: str, budget: int) -> dict:
    cmd = ['zg', 'query', *ROUTES[route], query, '--limit', str(budget),
           '--preview', 'none', '--refresh', 'off', '-g', '*.md']
    for glob in EXCLUDES:
        cmd.extend(['-g', glob])
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    result = {'command': cmd, 'stdout': proc.stdout, 'stderr': proc.stderr, 'returncode': proc.returncode}
    if proc.returncode:
        result['error'] = f'zg exited {proc.returncode}'
    else:
        try:
            result['raw_hits'] = parse_hits(proc.stdout)
        except ValueError as e:
            result['error'] = str(e)
    return result


def average(rows: list[dict]) -> dict:
    return {name: sum(row[name] for row in rows) / len(rows) if rows else None for name in METRICS}


def summarize(rows: list[dict], routes: list[str]) -> dict:
    summary = {}
    # Failure of any route invalidates the comparison, never a changing denominator.
    for route in routes:
        errors = sum('error' in row['routes'][route] for row in rows)
        scored = [row for row in rows if row['kind'] != 'distractor']
        valid = not errors
        kinds = sorted({row['kind'] for row in scored})
        summary[route] = {
            'valid': valid, 'attempted': len(rows), 'errors': errors, 'n': len(scored),
            'overall': average([row['routes'][route]['metrics'] for row in scored]) if valid else None,
            'by_kind': {kind: {'n': sum(row['kind'] == kind for row in scored),
                              'metrics': average([row['routes'][route]['metrics'] for row in scored if row['kind'] == kind])}
                        for kind in kinds} if valid else {},
            'underfilled_at_10': sum(len(row['routes'][route].get('hits', [])) < 10 for row in scored),
        }
    return summary


def fmt(value) -> str:
    return '—' if value is None else f'{value:.3f}'


def render(payload: dict) -> str:
    lines = [f"# {payload['eval']}", '', f"- time: {payload['at']}",
             f"- valid: {payload['valid']}; document k=10; candidate budget={payload['candidate_budget']}",
             f"- corpus SHA256: `{payload['corpus']['sha256']}`", '',
             '| route | n | errors | Hit@1 | Primary@5 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for route, block in payload['summary'].items():
        values = block['overall'] or dict.fromkeys(METRICS)
        lines.append(f"| {route} | {block['n']} | {block['errors']} | " + ' | '.join(fmt(values[n]) for n in METRICS) + ' |')
    for kind in sorted({q['kind'] for q in payload['items']} - {'distractor'}):
        lines += ['', f'## {kind}', '', '| route | n | Hit@1 | Primary@5 | Recall@5 | nDCG@10 |', '|---|---:|---:|---:|---:|---:|']
        for route, block in payload['summary'].items():
            sub = block['by_kind'].get(kind)
            if sub:
                lines.append(f"| {route} | {sub['n']} | " + ' | '.join(fmt(sub['metrics'][n]) for n in ['hit_at_1', 'primary_at_5', 'recall_at_5', 'ndcg_at_10']) + ' |')
    lines += ['', '## Diagnostics', '']
    for route, block in payload['summary'].items():
        lines.append(f"- {route}: scored queries with fewer than 10 unique documents: {block['underfilled_at_10']}")
    for q in payload['items']:
        if q['kind'] == 'distractor':
            for route, result in q['routes'].items():
                hits = result.get('hits', [])
                lines.append(f"- {q['id']} / {route}: {len(hits)} documents; top={hits[0]['path'] if hits else '(empty)'}; diagnostic only, no abstention metric")
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', type=int, default=10, choices=[10])
    parser.add_argument('--candidate-budget', type=int, default=100)
    parser.add_argument('--routes', default='hybrid,fts,vector')
    parser.add_argument('--ids', default='')
    args = parser.parse_args()
    routes = [r.strip() for r in args.routes.split(',')]
    if not routes or len(set(routes)) != len(routes) or any(r not in ROUTES for r in routes):
        parser.error('routes must be a nonempty unique subset of hybrid,fts,vector')
    if args.candidate_budget < 10:
        parser.error('candidate budget must be >=10')
    spec = json.loads(QUERIES.read_text())
    corpus = corpus_snapshot()
    validate_spec(spec, corpus)
    want = set(filter(None, (s.strip() for s in args.ids.split(','))))
    if want - {q['id'] for q in spec['queries']}:
        parser.error('unknown query ids: ' + ','.join(sorted(want - {q['id'] for q in spec['queries']})))
    queries = [q for q in spec['queries'] if not want or q['id'] in want]
    manifest_path = ROOT / '.zvec-grep/manifest.json'
    manifest_before = manifest_path.read_bytes()
    manifest = json.loads(manifest_before)
    if not all('!eval/**' in root.get('globs', []) for root in manifest['rootPaths']):
        parser.error('index roots must exclude eval/**; rebuild index first')
    version = subprocess.check_output(['zg', '--version'], text=True).strip()
    status = subprocess.check_output(['zg', 'status'], cwd=ROOT, text=True)
    run_dir = RUNS / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run_dir.mkdir(parents=True)
    (run_dir / 'queries.json').write_bytes(QUERIES.read_bytes())
    (run_dir / 'run.py').write_bytes(Path(__file__).read_bytes())
    payload = {'eval': spec['name'], 'at': datetime.now(timezone.utc).isoformat(), 'k': 10,
               'candidate_budget': args.candidate_budget, 'routes': routes, 'cwd': str(ROOT),
               'zg_version': version, 'index_manifest': manifest, 'index_status': status,
               'queries_sha256': digest(QUERIES.read_bytes()), 'runner_sha256': digest(Path(__file__).read_bytes()),
               'corpus': corpus, 'items': []}
    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {q['id']}", flush=True)
        item = {**q, 'routes': {}}
        for route in routes:
            result = {}
            try:
                result = run_zg(q['query'], route, args.candidate_budget)
                if 'error' not in result:
                    docs = document_hits(result['raw_hits'], corpus)
                    result['unique_candidate_count'] = len(docs)
                    result['hits'] = docs[:10]
                    result['metrics'] = metrics_for(result['hits'], q['relevant'])
            except (OSError, subprocess.SubprocessError, ValueError) as e:
                result['error'] = str(e)
            item['routes'][route] = result
            print(f"  {route}: " + (result['error'] if 'error' in result else f"{len(result['hits'])} docs; Primary@5={fmt(result['metrics']['primary_at_5'])}"), flush=True)
        payload['items'].append(item)
        (run_dir / 'checkpoint.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    payload['summary'] = summarize(payload['items'], routes)
    payload['snapshot_unchanged'] = (manifest_before == manifest_path.read_bytes() and corpus['sha256'] == corpus_snapshot()['sha256'])
    payload['valid'] = payload['snapshot_unchanged'] and all(b['valid'] for b in payload['summary'].values())
    report = render(payload)
    for directory in [run_dir, RUNS]:
        (directory / 'latest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        (directory / 'latest.md').write_text(report)
    print(report)
    print(f'Artifacts: {run_dir}')
    if not payload['valid']:
        sys.exit(1)


if __name__ == '__main__':
    main()
