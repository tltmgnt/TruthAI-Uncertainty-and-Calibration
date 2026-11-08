# Methods and acceptance boundaries

This package measures binary probability quality on supplied finite observations.
It distinguishes computation, empirical interpretation and ResearchOS policy state.

Brier = mean((p-y)^2). Log loss = -mean(y log p + (1-y) log(1-p)), implemented
by the observed class to avoid undefined 0 log 0 terms. Zero probability assigned
to an observed class gives positive infinite loss; JSON retains a null value plus
an explicit status. No epsilon clipping changes the score.

ECE = sum over bins of (bin count / total count) times the absolute difference
between mean predicted probability and observed outcome frequency. Empty bins have
null means. ECE is descriptive and cannot certify calibration or compare models fairly
without a declared binning/evaluation protocol.

For split conformal binary sets, scores are p for outcome 0 and 1-p for outcome 1.
Sort calibration scores; use rank ceil((n+1)(1-alpha)), counting from 1. If rank is
greater than n, use an unbounded threshold and include both labels. Otherwise
include each candidate class when its score is <= the rank-selected score. Ties
are included. Empty sets are allowed. Decimal alpha is interpreted exactly for rank
calculation to avoid floating-point rank overshoot. Empirical coverage can fall below
the nominal level on a small test split; it is not a universal coverage guarantee.

The usual marginal split-conformal coverage statement requires exchangeability of
calibration and future test scores and a predictor fixed independently of that
calibration sample. Supplied IDs and histogram distances cannot check these assumptions.
Neither label-conditional, subgroup, sequential nor shifted-distribution coverage is
asserted. No calibration transform is fitted using the held-out evaluation labels.

Primary background: Brier, Verification of forecasts expressed in terms of probability,
Monthly Weather Review 78 (1950), 1–3; Gneiting and Raftery, Strictly Proper Scoring
Rules, Prediction, and Estimation, JASA 102 (2007), 359–378;
Angelopoulos and Bates, A Gentle Introduction to Conformal Prediction and
Distribution-Free Uncertainty Quantification (2021), https://arxiv.org/abs/2107.07511.
These methods are established techniques; this package does not claim their invention.

Before reporting benefit, freeze predictor/data versions, group-aware train/calibration/
evaluation splits, primary metrics, uncertainty analysis, comparison baselines and
practical improvement thresholds. Preserve failures and external adjudication separately.
ResearchOS support state concerns the recorded finite computation only. Actual domain
attack results and independently collected reproduction must be supplied and reviewed
before claiming broader assurance; software self-tests do not replace them.
