# TruthAI Uncertainty and Calibration

Offline binary probability evaluation with an executable ResearchOS evidence adapter,
versioned claim state, rejection ledger and exact replay bundles. This is a bounded
research implementation. It does not establish population calibration or independent
reproduction, fit a recalibration model, or authorize operational decisions.

## Install and run

Python 3.10 or later. The runtime uses only the standard library.

```bash
python -m pip install .
mkdir -p runs
uncertainty-calibration analyze examples/binary.json --output runs/example
uncertainty-calibration verify runs/example
python -m unittest discover -s tests -v
python tests/check_installed.py
```

Open `runs/example/review.html` for reliability bins, metrics and ResearchOS blockers.
Without installation, use `python -m uncertainty_calibration` from the checkout.
Output directories must be new and their parent must exist. Exit 0 means scoped
computation or exact replay succeeded; it never means the claim is ASSURED.
Invalid inputs, existing destinations and changed bundles return exit 2.
The example is synthetic and its timestamps describe a fixed historical assessment.
Supply explicit current assessment and expiry times for a new study; they are never
silently extended.

## Implemented metrics

| Measure | Meaning and limit |
| --- | --- |
| Brier score | Mean squared binary probability error |
| Log loss | Natural logarithm score; impossible outcomes produce null with explicit positive_infinity status, without clipping |
| Reliability bins and ECE | Equal-width probability bins and weighted absolute probability/frequency gaps; sensitive to bin choice |
| Abstention | Confidence-threshold acceptance fraction and accuracy among accepted predictions; no accepted predictions means null accuracy |
| Split conformal sets | Finite-sample quantile of calibration nonconformity scores, with empirical evaluation coverage and mean set size |
| Shift diagnostic | Histogram total-variation distance between supplied probability splits; descriptive, not a statistical test |

Predicting class 1 uses probability >= 0.5. Abstention uses max(p,1-p) >= threshold.
Bins are left-inclusive/right-exclusive except the final bin includes probability 1.
The conformal score is 1 minus the true-class probability. Its rank is
ceil((n+1)(1-alpha)); rank above n includes both labels. The predictor and all
evaluation choices must be fixed before held-out scoring. See [methods](docs/METHODS.md).

## Input contract

See [the complete example](examples/binary.json). Required top-level fields are
`schema_version`, `label`, `calibration`, `evaluation`, `bins`, `alpha`,
`abstention_threshold`, `as_of` and `expires_at`. Each split contains 1–10000 rows
with unique `id`, finite `probability` in [0,1], and integer binary `outcome`.
IDs must be disjoint across splits. Inputs reject unknown fields, duplicate JSON
keys, nonfinite numbers and files above 8 MiB. ID separation cannot establish
absence of training leakage, group overlap or statistical dependence.

## ResearchOS integration

The repository vendors the six canonical v0.1.0 modules under a private namespace,
without editing their bytes. [researchos-lock.json](researchos-lock.json) pins the
source commit and SHA-256 release manifest. A conformance test checks every module.
This avoids the conflicting shared import/command names used by some domain repositories.
The adapter uses the real canonical Controller and replay implementation, not a mock.

The claim records a scoped computation. Actual summary bytes, input digest and metric
digest become validation evidence. Adjacent state transitions reach ADVERSARIAL_TEST;
the attempted REPRODUCED transition remains UNCERTAIN because independent reproduction
and required domain attacks are absent. No artificial reproduction receipts are supplied.
Policy confidence/density/independence values are declared weights, not calibrated
probabilities or proof of scientific independence. Actor names are not authenticated identities.

Each bundle captures input, metrics, scenario, ledger, controller report, escaped HTML
and a manifest of content and implementation hashes. Verification recomputes domain
metrics and controller transitions and compares every byte. Rehashing an edited result
cannot make it pass. This detects inconsistency with the installed implementation;
it does not authenticate supplied outcomes, preserve external custody or prevent someone
creating a different internally consistent study. Replay uses captured assessment time,
not present-day evidence validity, and requires identical code/numerical behavior.

## Tests and remaining work

Tests cover hand-calculated scores, endpoint probabilities, infinite loss, conformal
quantile boundaries, abstention, malformed data, canonical core conformance, ResearchOS
role/digest/expiry rejection, revision invalidation, replay tampering and installed CLI use.
CI runs supported Python versions and publishes only a synthetic example report.

Multiclass/regression scoring, fitted recalibrators, confidence intervals, formal
verification, group-aware evaluation, powered shift tests, real datasets and independent
studies remain future work. There is no clinical, financial or equipment execution path.
The existing Apache-2.0 license is retained; the vendored canonical code is from the
Apache-2.0 ResearchOs repository.

**∞**

## Topology compatibility and curriculum

See the [repository-specific v2 curriculum](docs/portfolio/TOPOLOGY_CURRICULUM_V2.md) for the minimum useful mathematics, six-criterion compatibility scorecard, source-linked exercises and adoption boundaries.
