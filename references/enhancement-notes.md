# Enhancement Notes

## Why this skill is stronger than the original prompt

The original prompt is already directionally strong. Its main limitation is that it compresses several distinct epistemic tasks into one loop:
- evidence discovery
- expert generation
- hypothesis generation
- confidence assignment
- convergence detection
- action recommendation

That makes it powerful, but also fragile. This skill separates those layers and makes them auditable.

## Main upgrades

### Flow and stocks
The ontology explicitly models entities, states, flows, stocks, and tests so the engine can reason about accumulation, bottlenecks, lag, and feedback rather than only static observations.

### Convergence rate
The skill tracks:
- entropy by round
- posterior drift by round
- effective number of viable hypotheses
- stability over consecutive rounds

This allows the system to distinguish true convergence from premature lock-in.

### Confidence intervals and robustness bands
Instead of presenting a single confidence number only, the skill can estimate:
- Wilson intervals for binomial-style support rates
- percentile bands from Monte Carlo simulation
- scenario robustness of the dominant baseline

### Bayesian structure
The skill treats priors, likelihoods, and posteriors explicitly. This helps separate:
- prior dominance
- evidence-driven shifts
- contradiction penalties
- posterior stability

### Monte Carlo stress testing
The Monte Carlo layer asks whether the baseline remains dominant when uncertain inputs move within plausible bounds. This is useful when evidence strength is fuzzy or prevalence is uncertain.

### Semantic clustering
Cluster expert statements into themes to distinguish:
- real independent convergence
- source echoing
- competing causal frames
- fragmented disagreement

### Evidence taxonomy
All major claims are typed as:
- fact
- measurement
- expert opinion
- association
- correlation
- causal claim
- mechanistic rule
- assumption
- derived estimate

This prevents epistemic leakage where soft evidence is allowed to behave like hard evidence.

### Inline visuals and HTML artifact
The skill asks for compact inline visuals during execution, then a polished self-contained HTML report for substantial tasks.

## Future extension ideas
- Dynamic expert reweighting using calibration error across rounds
- Bayesian model averaging across expert-specific causal graphs
- Explicit causal DAG export to JSON or Mermaid
- Sensitivity decomposition by evidence class
- Network graph of expert agreement and contradiction
- Counterfactual action simulation for candidate interventions
- Scenario tree mode for policy or strategy use cases
- Time-series change-point module for telemetry-heavy domains
