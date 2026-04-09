---
name: moae-baseline-engine
description: Autonomous Mixture-of-Abductive-Experts reasoning engine for problems framed as DOMAIN plus BASELINE_HYPOTHESIS_TEMPLATE. Use when the user wants expert-mixture reasoning, abductive diagnosis, confidence-weighted narrowing, Bayesian or Monte Carlo support, convergence tracking, evidence classification, semantic clustering of expert views, inline visualisation, or an interactive HTML decision artifact.
license: MIT
compatibility: Requires Python 3 with standard library only for core execution. Optional use of numpy/pandas/scikit-learn if available, but bundled scripts degrade gracefully without them.
metadata:
  author: Perplexity Computer
  version: '1.1.1'
---

# MoAE Baseline Engine

## When to Use This Skill

Use this skill when the user provides or implies:
- A problem DOMAIN and a desired baseline conclusion template
- A need to combine multiple expert perspectives into one converged baseline explanation
- Diagnostic, investigative, root-cause, or scenario-evaluation work
- Requests for confidence estimates, priors, convergence rate, entropy reduction, or uncertainty bounds
- Requests to distinguish facts from associations, correlations, and causations
- Requests for visual narrowing traces, probability flows, or scenario simulation

Typical triggers:
- “Use a mixture of experts”
- “Converge on a baseline hypothesis”
- “Bayesian reasoning”
- “Show confidence intervals or Monte Carlo”
- “Cluster the expert opinions”
- “Separate facts from causal claims”
- “Give me an interactive report”

## Core Design Goal

Produce a baseline explanation that is not just plausible, but auditable.

The skill should:
- Build expert perspectives autonomously
- Track how evidence changes belief over time
- Separate mechanism confidence from magnitude confidence
- Distinguish observation from inference
- Show why alternatives were eliminated
- Surface uncertainty, stability, and model risk
- Generate both concise inline visual summaries and a polished HTML artifact
- Preserve general-purpose structure: case-specific ontology, scorecards, and system panels must be overlays, not domain assumptions baked into the skill
- Distinguish posterior confidence from Monte Carlo finish-frequency so simulated dominance is not misread as certainty
- Prefer high-signal visual encodings such as colored bars, scorecards, and typed-relation highlighting when they materially improve cognition

## Required Inputs

Minimum user input:
1. DOMAIN = free-text description of the problem area
2. BASELINE_HYPOTHESIS_TEMPLATE = exact desired final baseline wording or template

Optional user input if volunteered:
- Observations or data
- Candidate actions
- Constraints
- User-supplied priors, expert sets, or thresholds

Do not ask for expert lists, priors, ontologies, thresholds, or knowledge bases unless the ambiguity is genuinely blocking progress.

## Mandatory Workflow

Follow this order. Do not skip steps.

### 1) Clarify only if ambiguity is truly blocking
- Ask at most 2 short questions.
- If the DOMAIN is usable, proceed.
- Default to action over questioning.

### 2) Frame the inference problem
Construct a compact problem frame:
- Decision objective
- Candidate baseline instantiations implied by the template
- Observable variables
- Hidden states
- Available evidence channels
- Actionability horizon
- Key asymmetries: false positive cost, false negative cost, delay cost, intervention cost

### 3) Build the ontology
Create a domain ontology with these minimum classes:
- Entities
- States
- Flows
- Stocks / accumulations
- Events
- Measurements / observations
- Hypotheses
- Tests / interventions
- Constraints
- Confounders
- Failure modes or mechanism classes

Add relations where possible:
- causes
- enables
- inhibits
- correlates-with
- associated-with
- contradicts
- measured-by
- updates-belief-in
- resolves-uncertainty-for

Prefer explicit typed relations over loose prose.

### 4) Auto-discover expert specialisations
Identify 4 to 8 expert viewpoints suited to the DOMAIN.
Examples:
- Mechanistic / physics expert
- Diagnostics / operations expert
- Reliability expert
- Controls expert
- Statistical inference expert
- Safety or compliance expert
- Market or behavioral expert
- Human factors expert

For each expert, create:
- Role name
- Scope of competence
- Signature failure modes / explanatory patterns
- Typical priors or prevalence assumptions
- Key discriminating observations
- Known blind spots

### 5) Classify evidence before using it
Every material claim must be assigned an evidence class:
- Fact
- Measurement
- Expert opinion
- Association
- Correlation
- Causal claim
- Mechanistic rule
- Assumption
- Derived estimate

Every claim should also receive:
- Reliability score from 0 to 1
- Direction of support: supports / weakly supports / neutral / weakly refutes / refutes
- Weight class: high / medium / low
- Provenance note

If a claim is causal, note whether causality is:
- Established
- Plausible but unproven
- Speculative

### 6) Initialise the expert mixture
Instantiate experts with an initial credibility weight αᵢ.
Default αᵢ values:
- Equal weights if evidence is limited
- Otherwise weight by source quality, scope fit, and historical relevance

Normalise weights so they sum to 1.

### 7) Generate initial hypotheses
Create a hypothesis set including:
- Baseline / null hypothesis
- Top competing mechanism hypotheses
- Mixed or interacting mechanism hypotheses if justified

For each hypothesis define:
- Description
- Required conditions
- Contradicting conditions
- Predicted observations
- Prior probability
- Mechanism confidence
- Magnitude confidence if quantitative outcomes are implied

### 8) Run the abductive convergence loop
Repeat until a termination condition is met.

Within each round:
1. Each expert ranks hypotheses with explanation traces.
2. Fuse expert rankings into a global posterior.
3. Adjust posterior using:
   - expert credibility αᵢ
   - evidence reliability
   - cross-expert consistency
   - contradiction penalties
   - novelty penalties for unsupported complexity
4. Prune logically impossible or strongly contradicted hypotheses.
5. Compute convergence diagnostics:
   - posterior entropy
   - effective number of viable hypotheses
   - posterior change from previous round
   - confidence interval width if probabilistic estimates exist
   - stability count across consecutive rounds
6. Identify highest-information-gain next test.
7. If interactive and a question materially reduces uncertainty, ask one question only.
8. Otherwise continue using available evidence or domain defaults.

### 9) Quantify uncertainty more rigorously when useful
Use bundled scripts where quantitative structure is possible.

#### Bayesian updating
Use for:
- Updating hypothesis probabilities from evidence likelihoods
- Combining priors with domain-specific prevalence or base rates
- Comparing posterior odds across competing explanations

#### Confidence intervals
Use for:
- Any rate, probability, prevalence, or scenario estimate that can be bounded
- Communicating uncertainty in expert-support shares or simulation outcomes

#### Monte Carlo
Use for:
- Uncertain priors
- Noisy observations
- Sensitivity analysis on threshold choices
- Estimating convergence robustness under uncertainty

The Monte Carlo pass should stress-test whether the selected baseline remains dominant under plausible perturbations.

When the domain has linked uncertainties, prefer correlated Monte Carlo over independent draws. Use shared factors or grouped correlation loadings when multiple priors or likelihoods should rise and fall together under the same latent driver.

When the decision is sensitive to hostile framing, worst-case assumptions, or strategic counter-moves, generate adversarial perturbation bands. At minimum, compare baseline, favorable, adverse, and severe-adverse cases for the dominant hypothesis.

Monte Carlo reporting rules:
- Report both posterior distribution summaries and winner-share finish frequency.
- Explicitly state that Monte Carlo winner share is the fraction of simulation draws in which a hypothesis finishes first, not the same thing as posterior confidence.
- If winner share is extreme while posterior intervals remain moderate, call that out as a parameterisation consequence and recommend widening priors or likelihood ranges if the user wants a harsher robustness test.
- Do not round extreme values so aggressively that 99.95% appears as a misleading 100.0% unless it is mathematically exact.

### 10) Semantic clustering of expert reasoning
Cluster expert explanation traces or evidence notes into themes such as:
- Strong consensus
- Weak consensus
- Polarised disagreement
- Independent corroboration
- Competing causal frames

Use clustering to show whether agreement arises from:
- Genuine independent convergence
- Repetition of the same source or idea
- Shared assumptions
- Different mechanisms implying similar observations

### 11) Inline visualisation during execution
When the medium supports it, include compact inline visuals such as:
- Posterior-by-round table or bar trace
- Entropy decline sparkline
- Confidence interval bands
- Expert weight drift summary
- Quadrant plot of confidence vs actionability
- Evidence map by class: fact / association / correlation / causation
- Sensitivity tornado summary

Keep inline visuals concise. The full visual treatment belongs in the HTML artifact.

### 12) Generate a polished HTML artifact when the task is substantial
For substantial cases, generate a self-contained HTML report with:
- Executive baseline card
- Expert mixture panel
- Evidence taxonomy panel
- Round-by-round narrowing trace
- Convergence chart
- Confidence interval view
- Monte Carlo distribution and percentile bands
- Correlated-uncertainty metadata when shared factors are used
- Adversarial perturbation band summaries when hostile or worst-case scenarios materially affect the decision
- Semantic cluster map of expert views
- Alternative hypotheses comparison matrix
- Recommended tests and actions
- Method notes and model caveats
- A date label in neutral universal format when a report date is available
- High-impact colored bar panels for posterior, Monte Carlo finish frequency, evidence classes, and any scorecards where bars improve scanability
- Typed-relation tables with relation-type color cues for faster cognition
- A source-universe panel that distinguishes analysed source pool from the final cited evidence register when source metadata is available
- Sensible source-universe fallbacks when the case is based on attached files, synthetic briefs, or local evidence rather than web research, avoiding misleading zero-count displays unless zero is truly known
- Optional weighted symbolic or decision scorecards with trend arrows when the case benefits from a compact metric composite

If bundled Python scripts are available, prefer using them to create the data package and HTML output.

### 13) Termination conditions
Stop when any is true:
- One hypothesis instantiates the BASELINE_HYPOTHESIS_TEMPLATE and exceeds the confidence threshold
- Only one viable hypothesis remains
- Entropy is below threshold
- Posterior is stable for 3 consecutive rounds
- Maximum iterations reached

Default parameters if not otherwise justified:
- CONFIDENCE_THRESHOLD = 0.90
- MAX_ITERATIONS = 12
- ENTROPY_THRESHOLD = 0.40
- STABILITY_ROUNDS = 3

### 14) Update expert credibility after the case
After the case, adjust expert credibility qualitatively:
- Increase αᵢ for experts whose hypotheses and discriminators aligned with the final outcome
- Decrease αᵢ for experts that overfit weak evidence or relied on contradicted assumptions

Do not claim durable learning across sessions unless persistence is actually available. Within-case adaptation is always allowed.

## Output Structure

Use this exact top-level structure in the user-facing answer:

**DOMAIN**: [restated]
**BASELINE HYPOTHESIS REACHED**: Yes / No
**FINAL BASELINE EXPLANATION**: [exact instantiation of the template]
**Confidence**: X.XX %
**Confidence Interval / Robustness Band**: [if available]
**Top 3 eliminated alternatives**: [one-sentence refutation each]
**Contributing Experts & Key Evidence**: [bullet list]
**Evidence Taxonomy Summary**: [facts vs associations vs correlations vs causal claims]
**Recommended Actions / Optimisations**: [if any]
**Narrowing Trace**: [round-by-round summary]
**Convergence Diagnostics**: [entropy, posterior stability, uncertainty notes]
**HTML Artifact**: [path or link if generated]

## Enhancement Ideas Embedded in This Skill

This skill explicitly improves the original prompt in these ways:
- Adds a typed ontology rather than only prose knowledge bases
- Separates evidence classes so weak associations do not masquerade as causal proof
- Distinguishes mechanism confidence from effect-size confidence
- Uses posterior stability and entropy together rather than confidence alone
- Adds confidence intervals and robustness bands
- Adds Monte Carlo stress testing for priors and uncertain evidence
- Adds semantic clustering to detect real convergence versus echoing
- Adds evidence weighting and contradiction penalties
- Adds compact inline visuals and a polished HTML report
- Adds explicit model-risk and caveat reporting
- Adds clearer distinction between posterior confidence and simulation finish frequency
- Adds visual scorecards, source-universe framing, and relation-type highlighting for faster analyst cognition

## Bundled Scripts

The skill includes executable Python utilities under `scripts/`.

### `scripts/probability_engine.py`
Use to:
- normalise priors
- perform Bayesian updates
- compute entropy
- compute posterior drift
- estimate simple confidence intervals

### `scripts/monte_carlo.py`
Use to:
- sample uncertain priors and likelihoods
- estimate robustness of the chosen baseline
- produce percentile summaries and sensitivity ranking
- model correlated uncertainty through shared factors or grouped correlation loadings
- generate adversarial perturbation bands across favorable, adverse, and severe-adverse scenarios

### `scripts/evidence_taxonomy.py`
Use to:
- validate evidence records
- classify evidence types
- aggregate weighted support by evidence class

### `scripts/semantic_cluster.py`
Use to:
- cluster expert statements or evidence notes
- surface consensus and disagreement themes
- produce cluster summaries

### `scripts/report_builder.py`
Use to:
- combine JSON inputs into a polished standalone HTML artifact
- render cards, charts, evidence bands, narrowing trace visuals, scorecards, source-universe metadata, and typed-relation color cues

## Execution Notes

- Prefer bundled scripts over ad hoc code when they fit.
- Keep code factored: data preparation, inference, simulation, and presentation should be separate concerns.
- If no quantitative data exists, still produce ordinal confidence and explain what would most increase precision.
- If sources conflict, represent the conflict explicitly.
- If the domain is highly sparse, state that confidence is dominated by prior structure rather than evidence.
- If correlated or adversarial Monte Carlo is not used, briefly justify why independent sampling is sufficient.

## Minimal Working Pattern

1. Restate DOMAIN and template.
2. Build ontology and expert set.
3. Create evidence table with classes and weights.
4. Generate hypotheses and priors.
5. Run one or more Bayesian update rounds.
6. If uncertainty remains, run Monte Carlo robustness analysis.
7. If key uncertainties are linked, run correlated Monte Carlo using shared factors or grouped loadings.
8. If strategic downside matters, generate adversarial perturbation bands.
9. Cluster expert views.
10. Produce inline visuals.
11. Produce HTML artifact for substantial tasks.
12. Return the exact output structure.

## Example Trigger

User input:
- DOMAIN: Fault detection and energy optimisation in large-scale commercial HVAC systems using telemetry data
- BASELINE_HYPOTHESIS_TEMPLATE: The system is operating normally with no fault, or confirmed root cause is fault X with ≥90% confidence

Expected behaviour:
- The skill auto-discovers relevant HVAC experts
- Builds evidence classes from telemetry and domain rules
- Runs abductive narrowing with priors and contradiction checks
- Produces confidence, eliminated alternatives, diagnostics, and an HTML artifact

## Guardrails

- Do not present correlation as causation.
- Do not hide uncertainty behind precise-looking percentages.
- Do not display long raw floating-point diagnostics in end-user artifacts; round diagnostics and counts to readable precision unless exact machine output is explicitly requested.
- Do not allow a single weak evidence strand to dominate without justification.
- Do not ask the user for parameters you can infer or set sensibly.
- Do not skip the taxonomy step.
- Do not generate visuals that are merely decorative; every visual must answer a decision question.
