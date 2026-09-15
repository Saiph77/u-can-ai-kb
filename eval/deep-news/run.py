#!/usr/bin/env python3
"""Deep News baseline: topical relevance and publication-date requirements."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_PATH = ROOT / 'eval/zg/run.py'
module_spec = importlib.util.spec_from_file_location('zg_eval_core', BASE_PATH)
core = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(core)
RUNS = HERE / 'runs'
EXTRA_METRICS = ['task_success_at_5', 'window_primary_at_5', 'window_ndcg_at_10',
                 'outside_window_fraction_at_5', 'stage_coverage_at_5', 'all_stages_at_5',
                 'candidate_task_success']
METRICS = core.METRICS + EXTRA_METRICS


def publication_date(text: str) -> str:
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('missing frontmatter')
    front = text.split('\n---\n', 1)[0]
    values = re.findall(r'^date:\s*([^\n]+)$', front, re.MULTILINE)
    if len(values) != 1:
        raise ValueError('missing/duplicate publication date')
    value = values[0].strip().strip('\"\x27')
    return date.fromisoformat(value).isoformat()


def corpus_snapshot() -> dict:
    files, dates = {}, {}
    for p in sorted((ROOT / 'deep-news/articles').glob('*.md')):
        if p.is_symlink():
            raise ValueError(f'symlink not supported: {p}')
        raw = p.read_bytes()
        path = p.relative_to(ROOT).as_posix()
        files[path] = core.digest(raw)
        dates[path] = publication_date(raw.decode('utf-8'))
    if not files:
        raise ValueError('empty corpus')
    return {'files': files, 'dates': dates, 'canonical': {p:p for p in files},
            'sha256': core.digest(json.dumps(files, ensure_ascii=False, sort_keys=True).encode())}


def in_window(path: str, q: dict, corpus: dict) -> bool:
    return q['time']['start'] <= corpus['dates'][path] <= q['time']['end']


def validate(spec: dict, judgments: dict, corpus: dict) -> None:
    core.validate_spec(spec, corpus)
    if spec['k'] != 10 or spec['candidate_budget'] < 10:
        raise ValueError('invalid fixed budget')
    as_of = date.fromisoformat(spec['as_of']).isoformat()
    if max(corpus['dates'].values()) > as_of:
        raise ValueError('corpus has post-as_of articles; freeze a new dataset explicitly')
    for ref, evidence in judgments.items():
        path = evidence['path']
        if path not in corpus['files'] or not evidence['quote'] or not evidence['reason']:
            raise ValueError(f'invalid judgment: {ref}')
        text = (ROOT / path).read_text()
        if evidence['quote'] not in text or text[:text.index(evidence['quote'])].count('\n') + 1 != evidence['line']:
            raise ValueError(f'judgment evidence drift: {ref}')
    expected = {'latest':'window', 'historical':'window', 'current':'prefer_recent',
                'foundation':'none', 'evolution':'stages'}
    for q in spec['queries']:
        if q['as_of'] != as_of or expected.get(q['kind']) != q['time']['mode']:
            raise ValueError(f"invalid date/intent: {q['id']}")
        for gold in q['relevant']:
            evidence = judgments[gold['evidence_ref']]
            if gold['paths'] != [evidence['path']]:
                raise ValueError('gold/evidence path mismatch')
        mode = q['time']['mode']
        if mode in {'window','prefer_recent'}:
            start = date.fromisoformat(q['time']['start']).isoformat()
            end = date.fromisoformat(q['time']['end']).isoformat()
            if not start <= end <= as_of:
                raise ValueError('invalid date window')
            if not any(g['grade'] == 2 and in_window(g['paths'][0],q,corpus) for g in q['relevant']):
                raise ValueError('no primary gold in requested window')
        if mode == 'stages':
            stages = q['stages']
            paths = {p for g in q['relevant'] for p in g['paths']}
            used = set()
            if len(stages) < 2 or len({s['id'] for s in stages}) != len(stages):
                raise ValueError('invalid stages')
            for stage in stages:
                members = set(stage['paths'])
                if not members or not members <= paths or members & used:
                    raise ValueError('missing, unknown or overlapping stage documents')
                used.update(members)


def stage_coverage(hits: list[dict], q: dict) -> float:
    found = {h['path'] for h in hits}
    return sum(bool(found.intersection(s['paths'])) for s in q['stages']) / len(q['stages'])


def task_success(hits: list[dict], q: dict, corpus: dict) -> float:
    mode = q['time']['mode']
    if mode == 'stages':
        return float(stage_coverage(hits,q) == 1)
    found = {h['path'] for h in hits}
    return float(any(g['grade'] == 2 and any(p in found and (mode != 'window' or in_window(p,q,corpus))
                                          for p in g['paths']) for g in q['relevant']))


def metrics_for(docs: list[dict], q: dict, corpus: dict) -> dict:
    top = docs[:10]
    metrics = {**core.metrics_for(top,q['relevant']), **dict.fromkeys(EXTRA_METRICS)}
    metrics['task_success_at_5'] = task_success(top[:5],q,corpus)
    metrics['candidate_task_success'] = task_success(docs,q,corpus)
    if q['time']['mode'] in {'window','prefer_recent'}:
        gold = [g for g in q['relevant'] if in_window(g['paths'][0],q,corpus)]
        timed = core.metrics_for(top,gold)
        metrics['window_primary_at_5'] = timed['primary_at_5']
        metrics['window_ndcg_at_10'] = timed['ndcg_at_10']
        metrics['outside_window_fraction_at_5'] = (sum(not in_window(h['path'],q,corpus) for h in top[:5]) / len(top[:5])) if top else None
    if q['time']['mode'] == 'stages':
        metrics['stage_coverage_at_5'] = stage_coverage(top[:5],q)
        metrics['all_stages_at_5'] = float(metrics['stage_coverage_at_5'] == 1)
    return metrics


def run_query(query: str, route: str, budget: int) -> dict:
    cmd = ['zg','query',*core.ROUTES[route],query,'--limit',str(budget),
           '--preview','none','--refresh','off','-g','deep-news/articles/*.md','-g','!eval/**']
    proc = subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=120)
    result = {'command':cmd,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
    if proc.returncode:
        result['error'] = f'zg exited {proc.returncode}'
    else:
        try:
            result['raw_hits'] = core.parse_hits(proc.stdout)
        except ValueError as e:
            result['error'] = str(e)
    return result


def aggregate(items: list[dict], route: str) -> dict:
    errors = sum('error' in item['routes'][route] for item in items)
    block = {'n':len(items),'errors':errors,'metrics':None,'metric_n':{}}
    if not errors:
        values = {m:[item['routes'][route]['metrics'][m] for item in items
                     if item['routes'][route]['metrics'][m] is not None] for m in METRICS}
        block['metrics'] = {m:sum(xs)/len(xs) if xs else None for m,xs in values.items()}
        block['metric_n'] = {m:len(xs) for m,xs in values.items()}
    return block


def render(payload: dict) -> str:
    lines = ['# Deep News 专属评测', '', f"- UTC: {payload['at']}; as_of: {payload['as_of']}",
             f"- valid: {payload['valid']}; articles: {len(payload['corpus']['files'])}; queries: {len(payload['items'])}",
             f"- 每路线候选片段预算: {payload['candidate_budget']}; 排名单位: 文章; 排序: 原始基线，无时间加权",'']
    def table(label, blocks):
        lines.extend([f'## {label}', '', '| route | n | errors | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowPrimary@5 | StageCoverage@5 | AllStages@5 | CandidateTask |',
                      '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|'])
        keys = ['hit_at_1','primary_at_5','ndcg_at_10','task_success_at_5','window_primary_at_5','stage_coverage_at_5','all_stages_at_5','candidate_task_success']
        for route,b in blocks.items():
            m = b['metrics'] or dict.fromkeys(keys)
            lines.append(f"| {route} | {b['n']} | {b['errors']} | " + ' | '.join(core.fmt(m[k]) for k in keys) + ' |')
        lines.append('')
    table('全体（Task 随意图定义，优先看分组）',payload['summary'])
    for kind, blocks in payload['by_kind'].items():
        table(kind,blocks)
    lines += ['## 指标说明', '', '- Primary@5 只看主题相关；Task@5 对 latest/historical 还要求日期合规，对 evolution 要求覆盖所有阶段，对 current/foundation 只要求首选相关。',
              '- WindowPrimary@5：相关首选且在日期窗口内；只在 latest/current/historical 计算（每组 6 题，全体 18 题）。current 的时间仅为软偏好，不代表窗口外文章失效。',
              '- StageCoverage / AllStages：仅 evolution（6 题）；CandidateTask：固定 100 片段内的所有去重文章是否已满足任务。',
              '- JSON 保存每个指标的实际题数、窗口 nDCG、窗口外比例。空结果不能靠低窗口外比例获得任务成功。',
              '- 无金标文档按 0，不意味着已确认无关；6 个主题簇不构成 30 个独立随机样本。', '', '## 前五未满足任务的查询', '']
    for route in payload['routes']:
        failures = [q['id'] for q in payload['items'] if q['routes'][route].get('metrics',{}).get('task_success_at_5') == 0]
        lines.append(f"- {route}: {', '.join(failures) or '无'}")
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--routes',default='hybrid,fts,vector')
    parser.add_argument('--ids',default='')
    parser.add_argument('--validate-only',action='store_true')
    args = parser.parse_args()
    routes = args.routes.split(',')
    if not routes or len(routes) != len(set(routes)) or any(r not in core.ROUTES for r in routes):
        parser.error('invalid or duplicate routes')
    source_paths = [HERE/'queries.json',HERE/'judgments.json',Path(__file__),BASE_PATH]
    frozen = {str(p):p.read_bytes() for p in source_paths}
    spec = json.loads(frozen[str(HERE/'queries.json')])
    judgments = json.loads(frozen[str(HERE/'judgments.json')])
    corpus = corpus_snapshot()
    validate(spec,judgments,corpus)
    wanted = set(filter(None,args.ids.split(',')))
    if wanted - {q['id'] for q in spec['queries']}:
        parser.error('unknown query ids')
    queries = [q for q in spec['queries'] if not wanted or q['id'] in wanted]
    if args.validate_only:
        print(f"Validated: {len(queries)} queries, {len(judgments)} evidence documents, {len(corpus['files'])} articles")
        return
    manifest_path = ROOT/'.zvec-grep/manifest.json'
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    if not manifest['rootPaths'] or any('!eval/**' not in r.get('globs',[]) for r in manifest['rootPaths']):
        parser.error('index roots must exclude eval/**')
    run_dir = RUNS/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run_dir.mkdir(parents=True)
    for p in source_paths:
        (run_dir/('zg_core.py' if p == BASE_PATH else p.name)).write_bytes(frozen[str(p)])
    payload = {'eval':spec['name'],'at':datetime.now(timezone.utc).isoformat(),'as_of':spec['as_of'],
               'candidate_budget':spec['candidate_budget'],'routes':routes,'corpus':corpus,
               'source_sha256':{p.relative_to(ROOT).as_posix():core.digest(frozen[str(p)]) for p in source_paths},
               'index_manifest':manifest,'zg_version':subprocess.check_output(['zg','--version'],text=True).strip(),
               'index_status':subprocess.check_output(['zg','status'],cwd=ROOT,text=True),'items':[]}
    for i,q in enumerate(queries,1):
        print(f"[{i}/{len(queries)}] {q['id']}",flush=True)
        item = {**q,'routes':{}}
        for route in routes:
            result = {}
            try:
                result = run_query(q['query'],route,spec['candidate_budget'])
                if 'error' not in result:
                    docs = core.document_hits(result['raw_hits'],corpus)
                    for hit in docs:
                        hit['published_at'] = corpus['dates'][hit['path']]
                    result.update(hits=docs[:10],unique_candidate_count=len(docs),metrics=metrics_for(docs,q,corpus))
            except (OSError,subprocess.SubprocessError,ValueError) as e:
                result['error'] = str(e)
            item['routes'][route] = result
            print(f"  {route}: " + (result['error'] if 'error' in result else f"Primary@5={result['metrics']['primary_at_5']:.0f} Task@5={result['metrics']['task_success_at_5']:.0f}"),flush=True)
        payload['items'].append(item)
        (run_dir/'checkpoint.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    payload['summary'] = {r:aggregate(payload['items'],r) for r in routes}
    payload['by_kind'] = {kind:{r:aggregate([q for q in payload['items'] if q['kind'] == kind],r) for r in routes}
                          for kind in sorted({q['kind'] for q in queries})}
    payload['snapshot_unchanged'] = (corpus['sha256'] == corpus_snapshot()['sha256'] and manifest_raw == manifest_path.read_bytes()
                                     and all(p.read_bytes() == frozen[str(p)] for p in source_paths))
    payload['valid'] = payload['snapshot_unchanged'] and all(not b['errors'] for b in payload['summary'].values())
    report = render(payload)
    for directory in [run_dir,RUNS]:
        (directory/'latest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
        (directory/'latest.md').write_text(report)
    print(report)
    print(f'Artifacts: {run_dir}')
    if not payload['valid']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
