#!/usr/bin/env python3
"""Evidence taxonomy helpers for MoAE Baseline Engine."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from typing import Dict, List

VALID_CLASSES = {
    'fact',
    'measurement',
    'expert_opinion',
    'association',
    'correlation',
    'causal_claim',
    'mechanistic_rule',
    'assumption',
    'derived_estimate',
}

VALID_DIRECTIONS = {
    'supports',
    'weakly_supports',
    'neutral',
    'weakly_refutes',
    'refutes',
}

VALID_WEIGHTS = {'high', 'medium', 'low'}
WEIGHT_VALUES = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
DIRECTION_VALUES = {
    'supports': 1.0,
    'weakly_supports': 0.5,
    'neutral': 0.0,
    'weakly_refutes': -0.5,
    'refutes': -1.0,
}


def validate_record(record: Dict[str, object]) -> List[str]:
    errors = []
    if record.get('class') not in VALID_CLASSES:
        errors.append(f"Invalid class: {record.get('class')}")
    if record.get('direction') not in VALID_DIRECTIONS:
        errors.append(f"Invalid direction: {record.get('direction')}")
    if record.get('weight_class') not in VALID_WEIGHTS:
        errors.append(f"Invalid weight_class: {record.get('weight_class')}")
    reliability = record.get('reliability', 0)
    try:
        reliability = float(reliability)
    except Exception:
        errors.append(f"Invalid reliability: {record.get('reliability')}")
        reliability = 0.0
    if not 0.0 <= reliability <= 1.0:
        errors.append(f'Reliability out of range: {reliability}')
    if record.get('class') == 'causal_claim':
        if record.get('causality_status') not in {'established', 'plausible_but_unproven', 'speculative'}:
            errors.append('causal_claim requires causality_status')
    return errors


def aggregate(records: List[Dict[str, object]]) -> Dict[str, object]:
    totals = defaultdict(float)
    counts = defaultdict(int)
    support_by_class = defaultdict(float)
    for r in records:
        errors = validate_record(r)
        if errors:
            continue
        cls = r['class']
        score = float(r['reliability']) * WEIGHT_VALUES[r['weight_class']] * DIRECTION_VALUES[r['direction']]
        totals[cls] += score
        counts[cls] += 1
        support_by_class[cls] += max(score, 0.0)
    return {
        'counts_by_class': dict(counts),
        'net_support_by_class': dict(totals),
        'positive_support_by_class': dict(support_by_class),
    }


def summarise_strength(records: List[Dict[str, object]]) -> Dict[str, object]:
    valid = [r for r in records if not validate_record(r)]
    agg = aggregate(valid)
    total_weighted_support = sum(agg['positive_support_by_class'].values())
    return {
        'valid_records': len(valid),
        'invalid_records': len(records) - len(valid),
        'total_weighted_support': total_weighted_support,
        **agg,
    }


def _usage() -> str:
    return 'Usage: evidence_taxonomy.py summary <json-records>'


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == 'summary':
        records = json.loads(args[1])
        print(json.dumps(summarise_strength(records), indent=2))
    else:
        print(_usage())
        sys.exit(1)
