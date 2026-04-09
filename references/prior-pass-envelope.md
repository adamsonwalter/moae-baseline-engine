# Prior-pass envelope (optional downstream attachment)

The light router may place a compact summary of a completed MoAE run into a capability-neutral case field such as **`prior_passes.abductive_convergence`**. This file does **not** define a rigid JSON shape: downstream case schemas intentionally allow an open object so the baseline engine can evolve without cross-repo schema locks.

**Practical guidance:**

- Prefer attaching **audit artifacts** the skill already generates (e.g. interactive HTML, scorecards) by reference or hash if the case store supports blobs; otherwise include a **short structured stub** (converged baseline string, top eliminated alternatives, posterior vs Monte Carlo note) for the delivery layer to quote.
- Never embed other skills’ identifiers in this stub; describe outcomes in domain-neutral language or paste user-supplied **DOMAIN** labels only.
