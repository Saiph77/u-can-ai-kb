"""Deterministic strategy/module loading for the experiments package.

Modules are loaded by file path via importlib with stable, unique module
names (experiments_<dir>_<stem>).  This avoids collisions between the
several same-named run.py / strategy.py files and never mutates the old
evaluators' globals.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # experiments/common
EXPERIMENTS = HERE.parent                       # experiments/
EVAL_DIR = EXPERIMENTS.parent                   # eval/deep-news/
REPO_ROOT = EVAL_DIR.parents[1]

if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))           # enables `import experiments.*`

VARIANTS = {"a": "a_baseline", "b": "b_normalize",
            "c": "c_window", "d": "d_temporal"}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_eval_core():
    """eval/zg/run.py — pure parsing/aggregation/metrics helpers."""
    return load_module(REPO_ROOT / "eval/zg/run.py", "zg_eval_core")


def load_eval_deepnews():
    """eval/deep-news/run.py — dates, temporal metrics, validators.

    Its own internal import of zg core registers 'zg_eval_core' with the
    same loader mechanism; loading it through this function first keeps the
    module identity stable.
    """
    if "zg_eval_core" not in sys.modules:
        load_eval_core()
    return load_module(EVAL_DIR / "run.py", "deepnews_eval")


def load_strategy(variant: str):
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of "
                         f"{sorted(VARIANTS)}")
    directory = VARIANTS[variant]
    path = EXPERIMENTS / directory / "strategy.py"
    if not path.exists():
        raise ValueError(f"strategy not implemented yet: {path}")
    return load_module(path, f"experiments_{directory}_strategy")


def load_strategy_module(variant: str, stem: str):
    """Load a sibling module of a variant, e.g. load_strategy_module('d','recency')."""
    directory = VARIANTS[variant]
    path = EXPERIMENTS / directory / f"{stem}.py"
    if not path.exists():
        raise ImportError(f"missing module: {path}")
    return load_module(path, f"experiments_{directory}_{stem}")
