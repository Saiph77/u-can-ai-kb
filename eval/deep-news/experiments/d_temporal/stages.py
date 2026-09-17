"""D-stages: budget allocation and deterministic round-robin coverage merge."""
from __future__ import annotations


def allocate_budget(total: int, m: int) -> list[int]:
    """Even split with remainder to earlier stages: 100/3 -> [34,33,33]."""
    if not (2 <= m <= 5):
        raise ValueError(f"stages count {m} outside supported 2-5")
    base, extra = divmod(total, m)
    return [base + (1 if i < extra else 0) for i in range(m)]


def merge_stages(stage_docs: list[list[dict]]) -> list[dict]:
    """Round-robin merge preserving each stage's own order.

    Each input list contains ranked_documents of one stage call (already
    carrying provenance).  A path appearing in several stages keeps its
    first position and accumulates provenance entries.  All candidates are
    kept — truncation is the scorer's business.
    """
    merged: list[dict] = []
    by_path: dict[str, dict] = {}
    cursors = [0] * len(stage_docs)
    while True:
        progressed = False
        for i, docs in enumerate(stage_docs):
            while cursors[i] < len(docs):
                d = docs[cursors[i]]
                cursors[i] += 1
                progressed = True
                if d["path"] in by_path:
                    by_path[d["path"]]["provenance"].extend(d["provenance"])
                    continue
                nd = dict(d)
                nd["rank"] = len(merged) + 1
                by_path[d["path"]] = nd
                merged.append(nd)
                break
        if not progressed:
            break
    for nd in merged:
        nd["reason"] = "stage_coverage"
    return merged
