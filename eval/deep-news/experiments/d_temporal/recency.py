"""D-soft: interpretable recency re-ranking over the full candidate list.

    R = 1 / (rank_constant + original_rank)
    F = 2 ** (-age_days / half_life_days)
    S = R * (1 + weight * F)

Applied only to prefer_recent plans.  The candidate SET is unchanged —
this is a soft preference, not a cutoff.  weight=0 must reproduce the
original order exactly.
"""
from __future__ import annotations

from datetime import date

REQUIRED = {"enabled", "rank_constant", "half_life_days", "weight"}


def validate_soft_config(cfg: dict) -> None:
    unknown = set(cfg) - REQUIRED
    if unknown:
        raise ValueError(f"unknown soft config fields: {sorted(unknown)}")
    if cfg["half_life_days"] <= 0:
        raise ValueError("half_life_days must be > 0")
    if cfg["weight"] < 0:
        raise ValueError("weight must be >= 0")
    if cfg["rank_constant"] <= 0:
        raise ValueError("rank_constant must be > 0")


def rerank_recency(documents: list[dict], as_of: str, config: dict) -> list[dict]:
    """documents: ranked_documents in original order.  Returns a new list."""
    validate_soft_config(config)
    ref = date.fromisoformat(as_of)
    k, hl, w = config["rank_constant"], config["half_life_days"], config["weight"]
    if w == 0 or not config.get("enabled", True):
        return [dict(d) for d in documents]
    scored = []
    for d in documents:
        pub = date.fromisoformat(d["published_at"])
        age = (ref - pub).days
        if age < 0:
            raise ValueError(f"future publication date {d['published_at']} "
                             f"for {d['path']} (as_of={as_of})")
        original_rank = d["rank"]
        R = 1 / (k + original_rank)
        F = 2 ** (-age / hl)
        S = R * (1 + w * F)
        scored.append((S, original_rank, d["path"], d,
                       {"original_rank": original_rank, "R": R,
                        "age_days": age, "F": F, "S": S}))
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    out = []
    for i, (S, _, _, d, aux) in enumerate(scored, 1):
        nd = dict(d)
        nd.update(aux)
        nd["score"] = S
        nd["rank"] = i
        nd["reason"] = "recency_soft"
        out.append(nd)
    return out
