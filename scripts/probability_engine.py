#!/usr/bin/env python3
"""Probability and convergence utilities for the MoAE Baseline Engine.

Standard-library only implementation.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from typing import Dict, Iterable, List, Tuple


EPS = 1e-12


def normalize(probabilities: Dict[str, float]) -> Dict[str, float]:
    cleaned = {k: max(float(v), 0.0) for k, v in probabilities.items()}
    total = sum(cleaned.values())
    if total <= EPS:
        n = max(len(cleaned), 1)
        return {k: 1.0 / n for k in cleaned} if cleaned else {}
    return {k: v / total for k, v in cleaned.items()}


def bayes_update(priors: Dict[str, float], likelihoods: Dict[str, float]) -> Dict[str, float]:
    post = {}
    for h, p in priors.items():
        post[h] = max(p, 0.0) * max(likelihoods.get(h, 0.0), 0.0)
    return normalize(post)


def sequential_update(priors: Dict[str, float], evidence_likelihoods: List[Dict[str, float]]) -> Dict[str, float]:
    current = normalize(priors)
    for lk in evidence_likelihoods:
        current = bayes_update(current, lk)
    return current


def shannon_entropy(probabilities: Dict[str, float], base: float = 2.0) -> float:
    probs = normalize(probabilities)
    log = math.log2 if base == 2.0 else lambda x: math.log(x, base)
    return -sum(p * log(p) for p in probs.values() if p > EPS)


def effective_hypothesis_count(probabilities: Dict[str, float]) -> float:
    probs = normalize(probabilities)
    denom = sum(p * p for p in probs.values())
    return 1.0 / denom if denom > EPS else 0.0


def posterior_drift(prev: Dict[str, float], current: Dict[str, float]) -> float:
    keys = set(prev) | set(current)
    return 0.5 * sum(abs(prev.get(k, 0.0) - current.get(k, 0.0)) for k in keys)


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> Tuple[float, float]:
    if trials <= 0:
        return 0.0, 1.0
    phat = successes / trials
    denom = 1 + z * z / trials
    center = (phat + z * z / (2 * trials)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * trials)) / trials) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def percentile(values: Iterable[float], q: float) -> float:
    vals = sorted(float(v) for v in values)
    if not vals:
        raise ValueError('No values supplied')
    if q <= 0:
        return vals[0]
    if q >= 1:
        return vals[-1]
    idx = (len(vals) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return vals[lo]
    frac = idx - lo
    return vals[lo] * (1 - frac) + vals[hi] * frac


def summarize_distribution(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": percentile(values, 0.5),
        "p05": percentile(values, 0.05),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
        "p95": percentile(values, 0.95),
        "min": min(values),
        "max": max(values),
    }


def _usage() -> str:
    return (
        'Usage:\n'
        '  probability_engine.py entropy <json-probs>\n'
        '  probability_engine.py update <json-priors> <json-likelihoods>\n'
        '  probability_engine.py drift <json-prev> <json-current>\n'
        '  probability_engine.py interval <successes> <trials>'
    )


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(_usage())
        sys.exit(1)

    cmd = args[0]
    if cmd == 'entropy' and len(args) == 2:
        probs = json.loads(args[1])
        print(json.dumps({
            'entropy': shannon_entropy(probs),
            'effective_hypothesis_count': effective_hypothesis_count(probs),
        }, indent=2))
    elif cmd == 'update' and len(args) == 3:
        priors = json.loads(args[1])
        likelihoods = json.loads(args[2])
        print(json.dumps(bayes_update(priors, likelihoods), indent=2))
    elif cmd == 'drift' and len(args) == 3:
        prev = json.loads(args[1])
        current = json.loads(args[2])
        print(json.dumps({'posterior_drift': posterior_drift(prev, current)}, indent=2))
    elif cmd == 'interval' and len(args) == 3:
        successes = int(args[1])
        trials = int(args[2])
        lo, hi = wilson_interval(successes, trials)
        print(json.dumps({'lower': lo, 'upper': hi}, indent=2))
    else:
        print(_usage())
        sys.exit(1)
