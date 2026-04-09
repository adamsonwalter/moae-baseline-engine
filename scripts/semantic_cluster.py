#!/usr/bin/env python3
"""Simple semantic clustering for expert statements.

Uses token-overlap Jaccard similarity with agglomerative merging.
Standard-library only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from typing import Dict, List, Set

STOPWORDS = {
    'the','a','an','and','or','of','to','in','on','for','with','by','from','at','as','is','are','was','were','be','been',
    'this','that','these','those','it','its','their','there','into','than','then','if','but','not','can','could','should',
    'would','may','might','will','about','over','under','after','before','between','through','using','use'
}


def tokenize(text: str) -> Set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster_texts(items: List[Dict[str, str]], threshold: float = 0.25) -> Dict[str, object]:
    enriched = []
    for idx, item in enumerate(items):
        text = item.get('text', '')
        enriched.append({
            'id': item.get('id', f'item-{idx+1}'),
            'label': item.get('label', item.get('id', f'item-{idx+1}')),
            'text': text,
            'tokens': tokenize(text),
        })

    clusters: List[List[Dict[str, object]]] = []
    for item in enriched:
        best_idx = None
        best_score = 0.0
        for i, cluster in enumerate(clusters):
            cluster_tokens = set().union(*(m['tokens'] for m in cluster))
            score = jaccard(item['tokens'], cluster_tokens)
            if score > best_score:
                best_score = score
                best_idx = i
        if best_idx is not None and best_score >= threshold:
            clusters[best_idx].append(item)
        else:
            clusters.append([item])

    results = []
    for i, cluster in enumerate(clusters, start=1):
        all_tokens = Counter()
        for member in cluster:
            all_tokens.update(member['tokens'])
        top_terms = [t for t, _ in all_tokens.most_common(8)]
        results.append({
            'cluster_id': f'cluster-{i}',
            'size': len(cluster),
            'labels': [m['label'] for m in cluster],
            'top_terms': top_terms,
            'summary_hint': ' / '.join(top_terms[:4]) if top_terms else 'misc',
        })

    return {
        'cluster_count': len(results),
        'clusters': results,
    }


def _usage() -> str:
    return 'Usage: semantic_cluster.py cluster <json-items> [threshold]'


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) in {2, 3} and args[0] == 'cluster':
        items = json.loads(args[1])
        threshold = float(args[2]) if len(args) == 3 else 0.25
        print(json.dumps(cluster_texts(items, threshold), indent=2))
    else:
        print(_usage())
        sys.exit(1)
