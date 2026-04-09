#!/usr/bin/env python3
"""Monte Carlo robustness analysis for the MoAE Baseline Engine.

Supports:
- standard independent sampling
- shared-factor correlated uncertainty via per-spec loadings
- adversarial perturbation scenarios and scenario bands

This implementation stays standard-library only and is intentionally conservative:
correlation is introduced through bounded value-space shocks rather than exact copulas.
"""
from __future__ import annotations

import json
import math
import random
import sys
from typing import Any, Dict, List, Optional, Tuple

from probability_engine import normalize, bayes_update, percentile, summarize_distribution

DEFAULT_ITERATIONS = 5000
DEFAULT_SHOCK_SCALE = 0.35


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def sample_base_value(spec) -> float:
    if isinstance(spec, (int, float)):
        return float(spec)
    if not isinstance(spec, dict):
        raise ValueError(f'Unsupported spec: {spec!r}')
    dist = spec.get('dist', 'fixed')
    if dist == 'fixed':
        return float(spec['value'])
    if dist == 'uniform':
        return random.uniform(float(spec['low']), float(spec['high']))
    if dist == 'triangular':
        return random.triangular(float(spec['low']), float(spec['high']), float(spec['mode']))
    if dist == 'normal':
        val = random.gauss(float(spec['mean']), float(spec['sd']))
        if 'low' in spec:
            val = max(val, float(spec['low']))
        if 'high' in spec:
            val = min(val, float(spec['high']))
        return val
    if dist == 'beta':
        return random.betavariate(float(spec['a']), float(spec['b']))
    raise ValueError(f'Unknown distribution: {dist}')


def derive_bounds(spec, sampled_value: Optional[float] = None) -> Tuple[float, float]:
    if isinstance(spec, (int, float)):
        val = float(spec)
        return val, val
    if not isinstance(spec, dict):
        if sampled_value is None:
            return 0.0, 1.0
        return float(sampled_value), float(sampled_value)
    dist = spec.get('dist', 'fixed')
    if dist == 'fixed':
        val = float(spec['value'])
        return val, val
    if dist in {'uniform', 'triangular'}:
        return float(spec['low']), float(spec['high'])
    if dist == 'normal':
        mean = float(spec['mean'])
        sd = float(spec['sd'])
        low = float(spec.get('low', mean - 4 * sd))
        high = float(spec.get('high', mean + 4 * sd))
        return low, high
    if dist == 'beta':
        return 0.0, 1.0
    if sampled_value is None:
        return 0.0, 1.0
    return float(sampled_value), float(sampled_value)


def estimate_spread(spec) -> float:
    if isinstance(spec, (int, float)):
        return 0.0
    if not isinstance(spec, dict):
        return 0.0
    dist = spec.get('dist', 'fixed')
    if dist == 'fixed':
        return 0.0
    if dist == 'uniform':
        return float(spec['high']) - float(spec['low'])
    if dist == 'triangular':
        return float(spec['high']) - float(spec['low'])
    if dist == 'normal':
        return 4 * float(spec['sd'])
    if dist == 'beta':
        a = float(spec['a'])
        b = float(spec['b'])
        var = (a * b) / (((a + b) ** 2) * (a + b + 1))
        return math.sqrt(var)
    return 0.0


def sample_factor_values(factor_definitions: Optional[Dict[str, object]]) -> Dict[str, float]:
    if not factor_definitions:
        return {}
    values: Dict[str, float] = {}
    for name, spec in factor_definitions.items():
        if isinstance(spec, (int, float)):
            values[name] = float(spec)
            continue
        if isinstance(spec, dict) and 'dist' not in spec:
            merged = {'dist': 'normal', 'mean': 0.0, 'sd': 0.35, 'low': -1.0, 'high': 1.0}
            merged.update(spec)
            spec = merged
        base = sample_base_value(spec)
        low, high = derive_bounds(spec, base)
        values[name] = clamp(base, low, high)
    return values


def compute_correlation_signal(spec, factor_values: Dict[str, float]) -> float:
    if not isinstance(spec, dict) or not factor_values:
        return 0.0
    if 'factor_loadings' in spec:
        loadings = spec.get('factor_loadings', {}) or {}
        raw = sum(float(weight) * factor_values.get(name, 0.0) for name, weight in loadings.items())
        denom = sum(abs(float(weight)) for weight in loadings.values()) or 1.0
        strength = float(spec.get('correlation_strength', 1.0))
        return clamp((raw / denom) * strength, -1.0, 1.0)
    if 'correlation_group' in spec:
        group = spec.get('correlation_group')
        corr = float(spec.get('correlation', spec.get('correlation_strength', 1.0)))
        return clamp(corr * factor_values.get(group, 0.0), -1.0, 1.0)
    return 0.0


def round_specific_bias(adversarial_config: Dict[str, Any], round_index: Optional[int], label: str) -> float:
    if round_index is None:
        return 0.0
    item = adversarial_config.get('round_hypothesis_bias')
    if isinstance(item, list):
        idx = round_index - 1
        if 0 <= idx < len(item) and isinstance(item[idx], dict):
            return float(item[idx].get(label, 0.0))
    if isinstance(item, dict):
        return float((item.get(str(round_index)) or {}).get(label, 0.0))
    return 0.0


def compute_adversarial_signal(
    spec,
    label: str,
    round_index: Optional[int],
    adversarial_config: Optional[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> float:
    if not adversarial_config:
        return 0.0
    enabled = adversarial_config.get('enabled', True)
    if enabled is False:
        return 0.0
    context = context or {}
    strength = float(adversarial_config.get('strength', 0.0))
    if strength == 0.0:
        return 0.0
    exposure = 1.0
    if isinstance(spec, dict):
        exposure = float(spec.get('adversarial_exposure', 1.0))
    bias = float(adversarial_config.get('global_bias', 0.0))
    bias += float((adversarial_config.get('hypothesis_bias') or {}).get(label, 0.0))
    bias += round_specific_bias(adversarial_config, round_index, label)
    if isinstance(spec, dict) and spec.get('correlation_group'):
        bias += float((adversarial_config.get('group_bias') or {}).get(spec.get('correlation_group'), 0.0))

    mode = adversarial_config.get('mode', 'custom')
    dominant = context.get('dominant_hypothesis')
    runner_up = context.get('runner_up_hypothesis')
    target = adversarial_config.get('target_hypothesis', dominant)

    if mode == 'anti_dominant' and label == dominant:
        bias -= 1.0
    elif mode == 'pro_dominant' and label == dominant:
        bias += 1.0
    elif mode == 'anti_target' and label == target:
        bias -= 1.0
    elif mode == 'pro_target' and label == target:
        bias += 1.0
    elif mode == 'tilt_to_runner_up':
        if label == dominant:
            bias -= 1.0
        if label == runner_up:
            bias += 1.0

    direction = 1.0
    if isinstance(spec, dict):
        direction = float(spec.get('adversarial_direction', 1.0))
    return clamp(bias * strength * exposure * direction, -1.0, 1.0)


def apply_shocks(base_value: float, spec, total_signal: float) -> float:
    low, high = derive_bounds(spec, base_value)
    if high <= low:
        return base_value
    shock_scale = float(spec.get('shock_scale', DEFAULT_SHOCK_SCALE)) if isinstance(spec, dict) else DEFAULT_SHOCK_SCALE
    shift = total_signal * shock_scale * (high - low)
    return clamp(base_value + shift, low, high)


def sample_weighted_value(
    spec,
    label: Optional[str] = None,
    round_index: Optional[int] = None,
    factor_values: Optional[Dict[str, float]] = None,
    adversarial_config: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> float:
    base = sample_base_value(spec)
    corr_signal = compute_correlation_signal(spec, factor_values or {})
    adv_signal = compute_adversarial_signal(spec, label or '', round_index, adversarial_config, context)
    total_signal = clamp(corr_signal + adv_signal, -1.0, 1.0)
    return max(0.0, apply_shocks(base, spec, total_signal))


def sample_prob_map(
    spec_map: Dict[str, object],
    factor_values: Optional[Dict[str, float]] = None,
    adversarial_config: Optional[Dict[str, Any]] = None,
    round_index: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    sampled = {
        k: sample_weighted_value(v, label=k, round_index=round_index, factor_values=factor_values, adversarial_config=adversarial_config, context=context)
        for k, v in spec_map.items()
    }
    return normalize(sampled)


def run_simulation(
    prior_specs: Dict[str, object],
    likelihood_specs: List[Dict[str, object]],
    iterations: int = DEFAULT_ITERATIONS,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, object]:
    options = options or {}
    factor_definitions = options.get('factor_definitions') or {}
    adversarial_config = options.get('adversarial_config') or None
    context = options.get('context') or {}

    winners: List[str] = []
    final_probs: Dict[str, List[float]] = {k: [] for k in prior_specs}

    for _ in range(iterations):
        factor_values = sample_factor_values(factor_definitions)
        probs = sample_prob_map(prior_specs, factor_values=factor_values, adversarial_config=adversarial_config, round_index=0, context=context)
        for i, lk_specs in enumerate(likelihood_specs, start=1):
            sampled_lk = {
                k: sample_weighted_value(v, label=k, round_index=i, factor_values=factor_values, adversarial_config=adversarial_config, context=context)
                for k, v in lk_specs.items()
            }
            probs = bayes_update(probs, sampled_lk)
        winner = max(probs.items(), key=lambda kv: kv[1])[0]
        winners.append(winner)
        for k, v in probs.items():
            final_probs.setdefault(k, []).append(v)

    counts = {k: winners.count(k) for k in set(winners)}
    winner_probs = normalize(counts)
    summaries = {k: summarize_distribution(v) for k, v in final_probs.items()}
    winner_intervals = {
        k: {'p05': percentile(v, 0.05), 'p50': percentile(v, 0.50), 'p95': percentile(v, 0.95)}
        for k, v in final_probs.items() if v
    }
    dominant_hypothesis = max(winner_probs.items(), key=lambda kv: kv[1])[0] if winner_probs else None

    return {
        'iterations': iterations,
        'winner_share': winner_probs,
        'winner_counts': counts,
        'posterior_summaries': summaries,
        'posterior_intervals': winner_intervals,
        'dominant_hypothesis': dominant_hypothesis,
        'factor_definitions_used': factor_definitions,
        'adversarial_config_used': adversarial_config,
    }


def rank_input_sensitivity(
    prior_specs: Dict[str, object],
    likelihood_specs: List[Dict[str, object]],
    options: Optional[Dict[str, Any]] = None,
) -> List[Tuple[str, float]]:
    options = options or {}
    scores = []
    for name, spec in prior_specs.items():
        scores.append((f'prior:{name}', estimate_spread(spec)))
    for i, lk in enumerate(likelihood_specs, start=1):
        for name, spec in lk.items():
            scores.append((f'likelihood_round_{i}:{name}', estimate_spread(spec)))
    for factor_name, factor_spec in (options.get('factor_definitions') or {}).items():
        scores.append((f'factor:{factor_name}', estimate_spread(factor_spec)))
    adv = options.get('adversarial_config') or {}
    strength = float(adv.get('strength', 0.0)) if adv else 0.0
    if strength:
        scores.append(('adversarial:strength', strength))
    return sorted(scores, key=lambda x: x[1], reverse=True)


def infer_runner_up(simulation_result: Dict[str, Any]) -> Optional[str]:
    summaries = simulation_result.get('posterior_summaries', {})
    ranked = sorted(
        ((name, data.get('mean', 0.0)) for name, data in summaries.items()),
        key=lambda kv: kv[1],
        reverse=True,
    )
    return ranked[1][0] if len(ranked) > 1 else None


def merge_dicts(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            merged = dict(out[k])
            merged.update(v)
            out[k] = merged
        else:
            out[k] = v
    return out


def run_adversarial_perturbation_bands(
    prior_specs: Dict[str, object],
    likelihood_specs: List[Dict[str, object]],
    iterations: int = DEFAULT_ITERATIONS,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    options = options or {}
    baseline_options = dict(options.get('baseline_options') or {})
    baseline = run_simulation(prior_specs, likelihood_specs, iterations=iterations, options=baseline_options)
    dominant = baseline.get('dominant_hypothesis')
    runner_up = infer_runner_up(baseline)

    shared_options = dict(options.get('shared_options') or {})
    scenarios = options.get('scenarios') or [
        {'name': 'baseline', 'kind': 'baseline'},
        {'name': 'favorable', 'kind': 'scenario', 'adversarial_config': {'strength': 0.35, 'mode': 'pro_dominant'}},
        {'name': 'adverse', 'kind': 'scenario', 'adversarial_config': {'strength': 0.35, 'mode': 'tilt_to_runner_up'}},
        {'name': 'severe_adverse', 'kind': 'scenario', 'adversarial_config': {'strength': 0.70, 'mode': 'tilt_to_runner_up'}},
    ]

    scenario_results: List[Dict[str, Any]] = []
    for scenario in scenarios:
        name = scenario.get('name', 'scenario')
        if scenario.get('kind') == 'baseline':
            result = baseline
        else:
            scenario_options = merge_dicts(shared_options, scenario.get('options') or {})
            adv_cfg = merge_dicts(scenario_options.get('adversarial_config') or {}, scenario.get('adversarial_config') or {})
            scenario_context = merge_dicts(scenario_options.get('context') or {}, {
                'dominant_hypothesis': dominant,
                'runner_up_hypothesis': runner_up,
            })
            scenario_options['adversarial_config'] = adv_cfg
            scenario_options['context'] = scenario_context
            result = run_simulation(prior_specs, likelihood_specs, iterations=iterations, options=scenario_options)
        dominant_interval = (result.get('posterior_intervals') or {}).get(dominant, {}) if dominant else {}
        scenario_results.append({
            'name': name,
            'dominant_hypothesis': dominant,
            'runner_up_hypothesis': runner_up,
            'winner_share_of_dominant': float((result.get('winner_share') or {}).get(dominant, 0.0)) if dominant else 0.0,
            'posterior_mean_of_dominant': float(((result.get('posterior_summaries') or {}).get(dominant, {}) or {}).get('mean', 0.0)) if dominant else 0.0,
            'posterior_p05_of_dominant': float(dominant_interval.get('p05', 0.0)) if dominant_interval else 0.0,
            'posterior_p95_of_dominant': float(dominant_interval.get('p95', 0.0)) if dominant_interval else 0.0,
            'result': result,
        })

    winner_shares = [item['winner_share_of_dominant'] for item in scenario_results if dominant]
    mean_posteriors = [item['posterior_mean_of_dominant'] for item in scenario_results if dominant]
    p05s = [item['posterior_p05_of_dominant'] for item in scenario_results if dominant]
    p95s = [item['posterior_p95_of_dominant'] for item in scenario_results if dominant]

    return {
        'dominant_hypothesis': dominant,
        'runner_up_hypothesis': runner_up,
        'scenarios': scenario_results,
        'winner_share_band_for_dominant': {
            'min': min(winner_shares) if winner_shares else 0.0,
            'max': max(winner_shares) if winner_shares else 0.0,
        },
        'posterior_mean_band_for_dominant': {
            'min': min(mean_posteriors) if mean_posteriors else 0.0,
            'max': max(mean_posteriors) if mean_posteriors else 0.0,
        },
        'posterior_interval_envelope_for_dominant': {
            'min_p05': min(p05s) if p05s else 0.0,
            'max_p95': max(p95s) if p95s else 0.0,
        },
    }


def _usage() -> str:
    return (
        'Usage:\n'
        '  monte_carlo.py run <json-prior-specs> <json-likelihood-specs> [iterations] [json-options]\n'
        '  monte_carlo.py sensitivity <json-prior-specs> <json-likelihood-specs> [json-options]\n'
        '  monte_carlo.py band <json-prior-specs> <json-likelihood-specs> [iterations] [json-options]'
    )


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(_usage())
        sys.exit(1)
    cmd = args[0]
    if cmd == 'run' and len(args) in {3, 4, 5}:
        priors = json.loads(args[1])
        likelihoods = json.loads(args[2])
        iterations = int(args[3]) if len(args) >= 4 else DEFAULT_ITERATIONS
        options = json.loads(args[4]) if len(args) == 5 else None
        print(json.dumps(run_simulation(priors, likelihoods, iterations, options=options), indent=2))
    elif cmd == 'sensitivity' and len(args) in {3, 4}:
        priors = json.loads(args[1])
        likelihoods = json.loads(args[2])
        options = json.loads(args[3]) if len(args) == 4 else None
        print(json.dumps(rank_input_sensitivity(priors, likelihoods, options=options), indent=2))
    elif cmd == 'band' and len(args) in {3, 4, 5}:
        priors = json.loads(args[1])
        likelihoods = json.loads(args[2])
        iterations = int(args[3]) if len(args) >= 4 else DEFAULT_ITERATIONS
        options = json.loads(args[4]) if len(args) == 5 else None
        print(json.dumps(run_adversarial_perturbation_bands(priors, likelihoods, iterations=iterations, options=options), indent=2))
    else:
        print(_usage())
        sys.exit(1)
