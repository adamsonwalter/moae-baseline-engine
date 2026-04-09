#!/usr/bin/env python3
"""Standalone HTML report builder for the MoAE Baseline Engine.

Input: JSON file containing report payload.
Output: self-contained HTML file.
"""
from __future__ import annotations

import html
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

CSS = """
:root {
  --bg: #171614;
  --surface: #1c1b19;
  --surface-alt: #22211f;
  --border: #4a4844;
  --text: #e2e0db;
  --muted: #b9b5ae;
  --primary: #4f98a3;
  --primary-2: #fdab43;
  --danger: #d163a7;
  --success: #6daa45;
  --warning: #d07b52;
  --purple: #8b72ff;
}
* { box-sizing: border-box; }
html { color-scheme: dark; background: var(--bg); }
body {
  margin: 0;
  padding: 28px;
  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
}
.container { max-width: 1460px; margin: 0 auto; }
.header { display: grid; grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr); gap: 18px; margin-bottom: 18px; }
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.18);
  min-width: 0;
}
.badge-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
.badge { display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 12px; border: 1px solid var(--border); color: var(--muted); }
.h1 { font-size: 34px; line-height: 1.12; margin: 0 0 10px; font-weight: 700; letter-spacing: -0.02em; }
.h2 { font-size: 20px; line-height: 1.2; margin: 0 0 12px; font-weight: 700; }
.h3 { font-size: 15px; line-height: 1.3; margin: 0 0 8px; font-weight: 700; color: var(--text); }
.sub { color: var(--muted); font-size: 14px; line-height: 1.6; }
.grid-4 { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:18px; margin-bottom:18px; }
.grid-3 { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:18px; margin-bottom:18px; }
.grid-2 { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:18px; margin-bottom:18px; }
.auto-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; }
.list { margin: 0; padding-left: 18px; line-height: 1.6; }
.small { font-size: 13px; color: var(--muted); line-height: 1.55; }
.kpi { display:flex; flex-direction:column; gap:8px; min-width:0; }
.kpi .label { color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi .value { font-size: 32px; font-weight:700; overflow-wrap:anywhere; }
.kpi .value.compact { font-size: 20px; line-height: 1.35; }
.stat-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; }
.stat { padding:12px; border-radius:14px; border:1px solid var(--border); background: rgba(255,255,255,0.015); }
.stat .label { color: var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:0.06em; }
.stat .value { font-size:22px; font-weight:700; margin-top:6px; overflow-wrap:anywhere; }
.bar-wrap { display:flex; flex-direction:column; gap:12px; }
.bar-row { display:grid; grid-template-columns:minmax(120px,220px) minmax(0,1fr) 82px; gap:12px; align-items:center; }
.bar-label { overflow-wrap:anywhere; color: var(--text); }
.bar { height:14px; background:#2b2927; border-radius:999px; overflow:hidden; border:1px solid rgba(255,255,255,0.08); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }
.bar > span { display:block; height:100%; background: linear-gradient(90deg, var(--primary), var(--primary-2)); border-radius:999px; }
.bar.secondary > span { background: linear-gradient(90deg, #8b72ff, #4f98a3); }
.bar.success > span { background: linear-gradient(90deg, #6daa45, #fdab43); }
.bar.danger > span { background: linear-gradient(90deg, #d163a7, #fdab43); }
.bar.note > span { background: linear-gradient(90deg, #4f98a3, #8b72ff); }
.table-wrap { overflow-x:auto; }
.matrix { width:100%; border-collapse:collapse; font-size:14px; }
.matrix th, .matrix td { border-bottom:1px solid var(--border); padding:10px 8px; text-align:left; vertical-align:top; }
.matrix th { color: var(--muted); font-weight:600; }
.spark-wrap { display:flex; flex-direction:column; gap:10px; }
.spark-svg { width:100%; height:auto; min-height:150px; border-radius:12px; background: var(--surface-alt); border:1px solid var(--border); display:block; }
.cluster { padding: 12px; border-radius: 14px; border: 1px solid var(--border); background: rgba(255,255,255,0.02); min-width: 0; }
.loop { padding:14px; border-radius:14px; border:1px solid var(--border); background: rgba(255,255,255,0.02); }
.footer-meta { margin-top: 18px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 12px; }
.footer-signoff { margin-top: 18px; color: var(--muted); font-size: 13px; line-height: 1.7; }
.footer-signoff a, .footer-meta a, .sources a { color: #b9d8ff; text-decoration: none; }
.pill { display:inline-block; padding:5px 9px; border-radius:999px; background:rgba(255,255,255,0.04); border:1px solid var(--border); color:var(--muted); font-size:12px; }
.rel-pill { display:inline-block; padding:5px 9px; border-radius:999px; font-size:12px; border:1px solid rgba(255,255,255,0.1); }
.rel-causes { background: rgba(208,123,82,0.18); color:#ffbc97; }
.rel-enables { background: rgba(109,170,69,0.18); color:#c6f08e; }
.rel-inhibits { background: rgba(209,99,167,0.18); color:#ffb2df; }
.rel-correlates-with, .rel-associated-with { background: rgba(79,152,163,0.18); color:#a8eef6; }
.rel-contradicts { background: rgba(209,99,167,0.22); color:#ffd2ec; }
.rel-measured-by { background: rgba(139,114,255,0.2); color:#d7c9ff; }
.rel-updates-belief-in { background: rgba(253,171,67,0.18); color:#ffd79f; }
.rel-resolves-uncertainty-for { background: rgba(79,152,163,0.18); color:#b6f2f7; }
.scorecard-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:14px; }
.scorecard-item { padding:14px; border-radius:14px; border:1px solid var(--border); background: rgba(255,255,255,0.02); }
.score-head { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; margin-bottom:8px; }
.score-name { font-weight:700; }
.score-meta { color: var(--muted); font-size: 12px; }
.score-value { font-size: 22px; font-weight:700; }
.trend-up { color:#fdab43; }
.trend-down { color:#d163a7; }
.trend-flat { color:#4f98a3; }
.source-list { margin:0; padding-left:18px; line-height:1.65; }
.source-list li { margin-bottom:6px; }
.note-callout { padding:12px 14px; border-radius:14px; border:1px solid var(--border); background: rgba(79,152,163,0.08); }
@media (max-width: 1100px) { .header, .grid-4, .grid-3, .grid-2 { grid-template-columns:1fr; } }
@media (max-width: 700px) { body { padding:16px; } .bar-row { grid-template-columns:1fr; } }
"""

JS = """
function enhanceInlineSvgs() {
  const svgs = document.querySelectorAll('[data-enhance-chart="true"]');
  svgs.forEach(svg => {
    svg.style.boxShadow = 'inset 0 1px 0 rgba(255,255,255,0.03)';
  });
}
window.addEventListener('DOMContentLoaded', enhanceInlineSvgs);
"""

RELATION_CLASS_MAP = {
    'causes': 'rel-causes',
    'enables': 'rel-enables',
    'inhibits': 'rel-inhibits',
    'correlates-with': 'rel-correlates-with',
    'associated-with': 'rel-associated-with',
    'contradicts': 'rel-contradicts',
    'measured-by': 'rel-measured-by',
    'updates-belief-in': 'rel-updates-belief-in',
    'resolves-uncertainty-for': 'rel-resolves-uncertainty-for',
}


def esc(text: Any) -> str:
    return html.escape(str(text))


def format_number(value: Any, digits: int = 3) -> str:
    try:
        val = float(value)
        formatted = f"{val:.{digits}f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted
    except Exception:
        return str(value)


def format_stat_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return 'n/a'
    try:
        val = float(value)
    except Exception:
        return str(value)
    return format_number(val, digits)


def normalize_report_date_label(value: Any) -> str:
    if value in (None, ''):
        return ''
    text = str(value).strip()
    months = {
        '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY', '06': 'JUN',
        '07': 'JUL', '08': 'AUG', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
    }
    parts = text.split('-')
    if len(parts) == 3 and len(parts[0]) == 4 and parts[1] in months:
        year, month, day = parts
        day = str(int(day))
        return f"{day}-{months[month]}-{year}"
    return text


def infer_source_universe(source_universe: Dict[str, Any], cited_evidence_register: List[Dict[str, Any]], internal_method_notes: List[str]) -> Dict[str, Any]:
    out = dict(source_universe or {})
    has_external = bool(cited_evidence_register)
    has_internal = bool(internal_method_notes)
    if 'cited_evidence_items' not in out or out.get('cited_evidence_items') in (None, ''):
        out['cited_evidence_items'] = len(cited_evidence_register)
    if has_external:
        if out.get('unique_external_items_analysed') in (None, '', 0):
            out['unique_external_items_analysed'] = len(cited_evidence_register)
        if out.get('search_results_reviewed') in (None, '', 0):
            out['search_results_reviewed'] = 'n/a'
        if out.get('fetched_documents_read') in (None, '', 0):
            out['fetched_documents_read'] = len(cited_evidence_register)
    elif has_internal:
        if out.get('unique_external_items_analysed') in (None, ''):
            out['unique_external_items_analysed'] = 'n/a'
        if out.get('search_results_reviewed') in (None, ''):
            out['search_results_reviewed'] = 'n/a'
        if out.get('fetched_documents_read') in (None, ''):
            out['fetched_documents_read'] = 'n/a'
    out.setdefault('sources_register_label', 'Cited evidence register')
    out.setdefault('method_notes_label', 'Internal mechanism and counterfactual notes')
    return out


def normalize_footer_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    profile = dict(profile or {})
    if not profile:
        return profile
    profile.setdefault('year', '2026')
    profile.setdefault('name', 'Walter Adamson')
    profile.setdefault('line_1', 'BHP 20yrs — Head IT Audit, IT Strategy, Corporate Planning, VP International')
    profile.setdefault('email', 'walter@outcomesnow.com')
    profile.setdefault('linkedin_url', 'https://linkedin.com/in/adamson')
    profile.setdefault('linkedin_label', 'linkedin.com/in/adamson')
    return profile


def format_percent(raw_value: float) -> str:
    pct = raw_value * 100.0
    if abs(pct) >= 99.95 and abs(pct) < 100.0:
        return f"{pct:.2f}%"
    if 0 < abs(pct) < 0.1:
        return f"{pct:.3f}%"
    return f"{pct:.1f}%"


def bar_rows(mapping: Dict[str, float], pct: bool = True, style: str = 'default') -> str:
    rows = []
    max_non_pct = max([float(v) for v in mapping.values()], default=1.0)
    for key, value in sorted(mapping.items(), key=lambda kv: kv[1], reverse=True):
        raw_value = float(value)
        width = max(0.0, min(100.0, raw_value * 100 if pct else (raw_value / max_non_pct * 100 if max_non_pct > 0 else 0.0)))
        label = format_percent(raw_value) if pct else f"{raw_value:.3f}"
        bar_class = 'bar'
        if style == 'secondary':
            bar_class = 'bar secondary'
        elif style == 'success':
            bar_class = 'bar success'
        elif style == 'danger':
            bar_class = 'bar danger'
        elif style == 'note':
            bar_class = 'bar note'
        rows.append(
            f'<div class="bar-row"><div class="bar-label">{esc(key)}</div><div class="{bar_class}"><span style="width:{width:.2f}%"></span></div><div class="small">{esc(label)}</div></div>'
        )
    return '<div class="bar-wrap">' + ''.join(rows) + '</div>' if rows else '<div class="small">No data</div>'


def bullet_list(items: List[str]) -> str:
    if not items:
        return '<div class="small">No items</div>'
    return '<ul class="list">' + ''.join(f'<li>{esc(item)}</li>' for item in items) + '</ul>'


def svg_line_chart(values: Sequence[float], title: str, stroke: str) -> str:
    if not values:
        return '<div class="small">No chart data</div>'
    width, height = 760, 180
    pad_l, pad_r, pad_t, pad_b = 40, 18, 18, 28
    chart_w = width - pad_l - pad_r
    chart_h = height - pad_t - pad_b
    min_v = min(values)
    max_v = max(values)
    span = max(max_v - min_v, 1e-9)
    points: List[Tuple[float, float]] = []
    for i, v in enumerate(values):
        x = pad_l + (chart_w * (0.5 if len(values) == 1 else i / (len(values) - 1)))
        y = pad_t + chart_h - ((v - min_v) / span) * chart_h
        points.append((x, y))
    grid_lines = []
    labels = []
    for i in range(4):
        y = pad_t + chart_h * i / 3
        grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" stroke="rgba(255,255,255,0.16)" stroke-width="1" />')
        val = max_v - (span * i / 3)
        labels.append(f'<text x="8" y="{y+4:.1f}" fill="#b9b5ae" font-size="11">{html.escape(format_number(val, 2))}</text>')
    x_labels = []
    for i, (x, _) in enumerate(points, start=1):
        x_labels.append(f'<text x="{x:.1f}" y="{height-8}" text-anchor="middle" fill="#b9b5ae" font-size="11">R{i}</text>')
    polyline = ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)
    dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{stroke}" />' for x, y in points)
    return f'''<div class="spark-wrap"><svg class="spark-svg" data-enhance-chart="true" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}"><rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="#22211f" />{''.join(grid_lines)}{''.join(labels)}<polyline fill="none" stroke="{stroke}" stroke-width="3" points="{polyline}" />{dots}{''.join(x_labels)}</svg><div class="small">{esc(title)}</div></div>'''


def source_list_html(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<div class="small">No sources listed</div>'
    return '<ol class="source-list">' + ''.join(
        f'<li><a href="{esc(item.get("url", ""))}">{esc(item.get("label", item.get("url", "")))}</a></li>'
        for item in items
    ) + '</ol>'


def relation_cell(relation_type: str) -> str:
    cls = RELATION_CLASS_MAP.get(relation_type, '')
    if cls:
        return f'<span class="rel-pill {cls}">{esc(relation_type)}</span>'
    return esc(relation_type)


def trend_display(metric: Dict[str, Any]) -> str:
    trend = str(metric.get('trend', 'flat')).lower()
    arrow = metric.get('arrow')
    if not arrow:
        arrow = {'up': '↑', 'down': '↓', 'flat': '→'}.get(trend, '→')
    cls = {'up': 'trend-up', 'down': 'trend-down', 'flat': 'trend-flat'}.get(trend, 'trend-flat')
    return f'<span class="{cls}">{esc(arrow)} {esc(metric.get("trend_label", trend.title()))}</span>'


def scorecard_html(scorecard: Dict[str, Any]) -> str:
    metrics = scorecard.get('metrics', []) if scorecard else []
    if not metrics:
        return ''
    cards = []
    for metric in metrics:
        score = float(metric.get('score', 0))
        weight = float(metric.get('weight', 0))
        cards.append(
            f'''<div class="scorecard-item">
              <div class="score-head">
                <div>
                  <div class="score-name">{esc(metric.get('name', 'Metric'))}</div>
                  <div class="score-meta">Weight {weight:.0%}</div>
                </div>
                <div class="score-value">{score:.0f}</div>
              </div>
              <div style="margin-bottom:8px">{trend_display(metric)}</div>
              <div class="bar success"><span style="width:{max(0.0, min(100.0, score)):.2f}%"></span></div>
              <div class="small" style="margin-top:8px">{esc(metric.get('basis', ''))}</div>
            </div>'''
        )
    composite = scorecard.get('composite_score')
    composite_html = ''
    if composite is not None:
        composite_html = f'<div class="note-callout" style="margin-bottom:14px"><strong>{esc(scorecard.get("composite_label", "Composite symbolic score"))}:</strong> {esc(format_number(composite, 1))} / 100. {esc(scorecard.get("interpretation", ""))}</div>'
    return f'''<section class="card" style="margin-bottom:18px"><div class="h2">{esc(scorecard.get("title", "Scorecard"))}</div><div class="small" style="margin-bottom:12px">{esc(scorecard.get("description", ""))}</div>{composite_html}<div class="scorecard-grid">{''.join(cards)}</div></section>'''


def build_html(payload: Dict[str, Any]) -> str:
    domain = payload.get('domain', 'Unknown domain')
    final_explanation = payload.get('final_baseline_explanation', 'Not provided')
    confidence = float(payload.get('confidence', 0.0)) * 100
    ci = payload.get('confidence_interval') or {}
    entropy_series = payload.get('convergence', {}).get('entropy_by_round', [])
    drift_series = payload.get('convergence', {}).get('posterior_drift_by_round', [])
    experts = payload.get('experts', [])
    evidence_summary = payload.get('evidence_taxonomy_summary', {})
    alternatives = payload.get('eliminated_alternatives', [])
    narrowing = payload.get('narrowing_trace', [])
    posterior = payload.get('final_posterior', {})
    monte_carlo = payload.get('monte_carlo', {})
    winner_share = monte_carlo.get('winner_share', {})
    sensitivity = monte_carlo.get('sensitivity', [])
    clusters = payload.get('semantic_clusters', {}).get('clusters', [])
    actions = payload.get('recommended_actions', [])
    diagnostics = payload.get('convergence_diagnostics', {})
    baseline_reached = payload.get('baseline_hypothesis_reached', 'Not stated')
    report_date_label = normalize_report_date_label(payload.get('report_date_label'))
    footer_profile = normalize_footer_profile(payload.get('footer_profile', {}))
    source_universe = infer_source_universe(payload.get('source_universe', {}), payload.get('cited_evidence_register', []), payload.get('internal_method_notes', []))
    cited_evidence_register = payload.get('cited_evidence_register', [])
    internal_method_notes = payload.get('internal_method_notes', [])
    strategic_panel = payload.get('strategic_panel', {})
    ontology = payload.get('ontology', {})
    epistemic_notes = payload.get('epistemic_notes', {})
    scorecard = payload.get('symbolic_scorecard') or payload.get('decision_scorecard') or {}

    ci_text = 'Not estimated'
    if ci:
        ci_text = f"{float(ci.get('lower', 0))*100:.1f}% to {float(ci.get('upper', 0))*100:.1f}%"

    badge_row = '<div class="badge-row"><div class="badge">MoAE Baseline Engine</div>'
    if report_date_label:
        badge_row += f'<div class="badge">{esc(report_date_label)}</div>'
    badge_row += '</div>'

    expert_items = ''.join(
        f'<tr><td>{esc(e.get("name", "Expert"))}</td><td>{esc(e.get("scope", ""))}</td><td>{esc(e.get("credibility", ""))}</td><td>{esc(", ".join(e.get("blind_spots", [])))}</td></tr>'
        for e in experts
    ) or '<tr><td colspan="4" class="small">No expert details</td></tr>'

    alternative_items = ''.join(
        f'<tr><td>{esc(a.get("hypothesis", ""))}</td><td>{esc(a.get("refutation", ""))}</td></tr>'
        for a in alternatives
    ) or '<tr><td colspan="2" class="small">No eliminated alternatives provided</td></tr>'

    narrowing_items = ''.join(
        f'<tr><td>{esc(step.get("round", ""))}</td><td>{esc(step.get("summary", ""))}</td><td>{esc(step.get("remaining_hypotheses", ""))}</td></tr>'
        for step in narrowing
    ) or '<tr><td colspan="3" class="small">No narrowing trace provided</td></tr>'

    cluster_items = ''.join(
        f'<div class="cluster"><div class="h3">{esc(c.get("cluster_id", "Cluster"))}</div><div class="small">{esc(", ".join(c.get("labels", [])))}</div><div style="margin-top:8px">{esc(c.get("summary_hint", ""))}</div></div>'
        for c in clusters
    ) or '<div class="small">No clusters</div>'

    sensitivity_items = ''.join(
        f'<tr><td>{esc(name)}</td><td>{esc(format_number(score, 3))}</td></tr>' for name, score in sensitivity[:12]
    ) or '<tr><td colspan="2" class="small">No sensitivity analysis provided</td></tr>'

    loops_html = ''
    if strategic_panel.get('loops'):
        loops_html = ''.join(
            f'<div class="loop"><div class="h3">{esc(loop.get("name", "Loop"))} <span class="pill">{esc(loop.get("type", ""))}</span></div><div class="small">{esc(loop.get("mechanism", ""))}</div></div>'
            for loop in strategic_panel.get('loops', [])
        )

    relation_rows = ''
    if ontology.get('relations'):
        relation_rows = ''.join(
            f'<tr><td>{esc(r.get("from", ""))}</td><td>{relation_cell(str(r.get("type", "")))}</td><td>{esc(r.get("to", ""))}</td></tr>'
            for r in ontology.get('relations', [])
        )

    source_universe_html = ''
    if source_universe:
        source_universe_html = f'''<section class="card"><div class="h2">Source universe</div><div class="stat-grid"><div class="stat"><div class="label">Unique external items analysed</div><div class="value">{esc(source_universe.get('unique_external_items_analysed', 'n/a'))}</div></div><div class="stat"><div class="label">Search results reviewed</div><div class="value">{esc(source_universe.get('search_results_reviewed', 'n/a'))}</div></div><div class="stat"><div class="label">Fetched documents read</div><div class="value">{esc(source_universe.get('fetched_documents_read', 'n/a'))}</div></div><div class="stat"><div class="label">Cited evidence items</div><div class="value">{esc(source_universe.get('cited_evidence_items', 'n/a'))}</div></div></div><div class="small" style="margin-top:10px">This panel counts the analysed source universe separately from the narrower cited evidence register shown below.</div></section>'''

    footer_signoff_html = ''
    if footer_profile:
        footer_signoff_html = f'''<div class="footer-signoff"><div>© {esc(footer_profile.get("year", ""))} {esc(footer_profile.get("name", ""))}</div><div>{esc(footer_profile.get("line_1", ""))}</div><div><a href="mailto:{esc(footer_profile.get("email", ""))}">{esc(footer_profile.get("email", ""))}</a> &nbsp;&nbsp;·&nbsp;&nbsp; <a href="{esc(footer_profile.get("linkedin_url", ""))}">{esc(footer_profile.get("linkedin_label", footer_profile.get("linkedin_url", "")))}</a></div></div>'''

    winner_note = ''
    if winner_share:
        winner_note = '<div class="small" style="margin-top:10px">Dominant-hypothesis finish frequency across Monte Carlo draws. This is not the same thing as posterior confidence.</div>'

    evidence_panel = bar_rows(evidence_summary.get('positive_support_by_class', {}), pct=False, style='note')
    posterior_panel = bar_rows(posterior, pct=True, style='success')
    winner_panel = bar_rows(winner_share, pct=True, style='secondary')

    ontology_html = ''
    if ontology:
        ontology_html = f'''<div class="grid-2"><section class="card"><div class="h2">Tightened ontology</div><div class="auto-grid">{''.join([f'<div class="cluster"><div class="h3">{esc(title)}</div>{bullet_list(items)}</div>' for title, items in [("Sentiment formation pathway", ontology.get("sentiment_formation_pathway", [])), ("Symbolic victory metrics", ontology.get("symbolic_victory_metrics", [])), ("Stocks", ontology.get("stocks", [])), ("Flows", ontology.get("flows", [])), ("Measurements", ontology.get("measurements", [])), ("Constraints", ontology.get("constraints", []))] if items])}</div></section><section class="card"><div class="h2">Typed relations</div><div class="table-wrap"><table class="matrix"><thead><tr><th>From</th><th>Relation</th><th>To</th></tr></thead><tbody>{relation_rows or '<tr><td colspan="3" class="small">No typed relations provided</td></tr>'}</tbody></table></div></section></div>'''

    strategic_html = ''
    if strategic_panel:
        strategic_html = f'''<section class="card" style="margin-bottom:18px"><div class="h2">{esc(strategic_panel.get("title", "Strategic panel"))}</div><div class="small" style="margin-bottom:10px">{esc(strategic_panel.get("question", ""))}</div><div style="margin-bottom:14px">{esc(strategic_panel.get("thesis", ""))}</div><div class="auto-grid" style="margin-bottom:14px">{loops_html}</div><div class="small"><strong>Decision rule:</strong> {esc(strategic_panel.get("decision_rule", ""))}</div></section>'''

    epistemic_html = ''
    if epistemic_notes:
        epistemic_html = f'''<section class="card"><div class="h2">Epistemic position</div><ul class="list"><li>Mechanism confidence: {esc(epistemic_notes.get("mechanism_confidence", "n/a"))}</li><li>{esc(epistemic_notes.get("interpretation", ""))}</li><li>{esc(epistemic_notes.get("analyst_note", ""))}</li></ul></section>'''

    sources_html = ''
    if cited_evidence_register or internal_method_notes:
        sources_html = f'''<div class="grid-2 sources"><section class="card"><div class="h2">{esc(source_universe.get("sources_register_label", "Cited evidence register"))}</div><div class="small" style="margin-bottom:10px">The items below are the external sources directly cited into the final reasoning record, distinct from the wider analysed source universe.</div>{source_list_html(cited_evidence_register)}</section><section class="card"><div class="h2">{esc(source_universe.get("method_notes_label", "Internal method notes"))}</div><div class="small" style="margin-bottom:10px">These are non-external reasoning artifacts used to structure the model rather than external sources.</div>{bullet_list(internal_method_notes)}</section></div>'''

    html_out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="dark" />
<meta name="description" content="MoAE Baseline Engine report" />
<title>MoAE Report</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
  <div class="header">
    <section class="card">
      {badge_row}
      <h1 class="h1">{esc(domain)}</h1>
      <div class="sub">{esc(final_explanation)}</div>
    </section>
    <section class="card">
      <div class="kpi"><div class="label">Confidence</div><div class="value">{confidence:.2f}%</div></div>
      <div class="kpi" style="margin-top:12px"><div class="label">Robustness band</div><div class="value compact">{esc(ci_text)}</div></div>
    </section>
  </div>

  <section class="card" style="margin-bottom:18px">
    <div class="stat-grid">
      <div class="stat"><div class="label">Baseline reached</div><div class="value">{esc(baseline_reached)}</div></div>
      <div class="stat"><div class="label">Final entropy</div><div class="value">{esc(format_stat_value(diagnostics.get('final_entropy', 'n/a'), 3))}</div></div>
      <div class="stat"><div class="label">Effective viable hypotheses</div><div class="value">{esc(format_stat_value(diagnostics.get('effective_hypothesis_count', 'n/a'), 3))}</div></div>
      <div class="stat"><div class="label">Termination reason</div><div class="value">{esc(diagnostics.get('termination_reason', 'n/a'))}</div></div>
    </div>
  </section>

  <div class="grid-4">
    <section class="card"><div class="h2">Final posterior</div>{posterior_panel}</section>
    <section class="card"><div class="h2">Monte Carlo winner share</div>{winner_panel}{winner_note}</section>
    <section class="card"><div class="h2">Evidence classes</div>{evidence_panel}</section>
    {source_universe_html or '<section class="card"><div class="h2">Source universe</div><div class="small">No source-universe metadata provided.</div></section>'}
  </div>

  {scorecard_html(scorecard)}

  <div class="grid-2">
    <section class="card"><div class="h2">Entropy by round</div>{svg_line_chart(entropy_series, 'Lower is better when narrowing toward a stable explanation.', '#4f98a3')}</section>
    <section class="card"><div class="h2">Posterior drift by round</div>{svg_line_chart(drift_series, 'Shows whether the posterior is still moving materially between rounds.', '#fdab43')}</section>
  </div>

  {strategic_html}

  <div class="grid-2">
    <section class="card"><div class="h2">Expert mixture</div><div class="table-wrap"><table class="matrix"><thead><tr><th>Expert</th><th>Scope</th><th>Credibility</th><th>Blind spots</th></tr></thead><tbody>{expert_items}</tbody></table></div></section>
    {epistemic_html or '<section class="card"><div class="h2">Epistemic position</div><div class="small">No epistemic notes provided.</div></section>'}
  </div>

  {ontology_html}

  <div class="grid-2">
    <section class="card"><div class="h2">Eliminated alternatives</div><div class="table-wrap"><table class="matrix"><thead><tr><th>Hypothesis</th><th>Refutation</th></tr></thead><tbody>{alternative_items}</tbody></table></div></section>
    <section class="card"><div class="h2">Recommended actions</div>{bullet_list(actions)}</section>
  </div>

  <div class="grid-2">
    <section class="card"><div class="h2">Narrowing trace</div><div class="table-wrap"><table class="matrix"><thead><tr><th>Round</th><th>Summary</th><th>Remaining</th></tr></thead><tbody>{narrowing_items}</tbody></table></div></section>
    <section class="card"><div class="h2">Input sensitivity</div><div class="table-wrap"><table class="matrix"><thead><tr><th>Input</th><th>Spread proxy</th></tr></thead><tbody>{sensitivity_items}</tbody></table></div></section>
  </div>

  <section class="card" style="margin-bottom:18px"><div class="h2">Semantic clusters</div><div class="auto-grid">{cluster_items}</div></section>

  {sources_html}

  {footer_signoff_html}

  <div class="footer-meta">Generated by the MoAE Baseline Engine as a general-purpose mixture-of-abductive-experts reasoning artifact. The ontology, scorecard, and system panels are case-specific overlays, not domain constraints on the skill.</div>
</div>
<script>{JS}</script>
</body>
</html>'''
    return html_out


def build_report(input_path: Path, output_path: Path) -> None:
    payload = json.loads(input_path.read_text(encoding='utf-8'))
    output_path.write_text(build_html(payload), encoding='utf-8')


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print('Usage: report_builder.py <input.json> <output.html>')
        return 1
    build_report(Path(argv[1]), Path(argv[2]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
