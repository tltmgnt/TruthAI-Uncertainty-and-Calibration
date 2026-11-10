# Topology compatibility and curriculum v2 — TruthAI-Uncertainty-and-Calibration

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | specialized evaluation |
| Minimum useful mathematics | Probability/statistics first; no additional topology required |
| Relationships to preserve | Calibration/evaluation split, probability values and metric definitions |
| Concrete operation / capstone | Hand-compute a two-row Brier score, vary reliability bins and explain why ECE changes |
| Necessity and scope boundary | Conformal coverage assumptions and descriptive metrics do not establish population calibration; TDA has no demonstrated necessity here |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with probability/statistics first and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify calibration/evaluation split, probability values and metric definitions. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain probability/statistics first; no additional topology required. | Hand-compute a two-row Brier score, vary reliability bins and explain why ECE changes. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `4bbfee3499ea4a56295b64312fb2750568b114eb` in [uncertainty_calibration/metrics.py](../../uncertainty_calibration/metrics.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [9](../../uncertainty_calibration/metrics.py#L9) | `def fields(obj, names):` | State the input/output contract and trace one normal and one failing case. |
| [11](../../uncertainty_calibration/metrics.py#L11) | `raise ValueError('Missing or unknown fields')` | Construct the triggering input and explain why rejection preserves the contract. |
| [14](../../uncertainty_calibration/metrics.py#L14) | `def probability(value):` | State the input/output contract and trace one normal and one failing case. |
| [16](../../uncertainty_calibration/metrics.py#L16) | `raise ValueError('Finite probability in [0,1] required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [17](../../uncertainty_calibration/metrics.py#L17) | `return value` | Predict the returned value and distinguish a computed result from authorization. |
| [20](../../uncertainty_calibration/metrics.py#L20) | `def validate(data):` | State the input/output contract and trace one normal and one failing case. |
| [21](../../uncertainty_calibration/metrics.py#L21) | `fields(data, ('schema_version', 'label', 'calibration', 'evaluation', 'bins',` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [23](../../uncertainty_calibration/metrics.py#L23) | `if type(data['schema_version']) is not int or data['schema_version'] != 1:` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [24](../../uncertainty_calibration/metrics.py#L24) | `raise ValueError('Unsupported schema version')` | Construct the triggering input and explain why rejection preserves the contract. |
| [26](../../uncertainty_calibration/metrics.py#L26) | `raise ValueError('Short nonempty dataset label required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [28](../../uncertainty_calibration/metrics.py#L28) | `raise ValueError('Between 2 and 50 bins required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [30](../../uncertainty_calibration/metrics.py#L30) | `raise ValueError('alpha must be strictly between zero and one')` | Construct the triggering input and explain why rejection preserves the contract. |
| [32](../../uncertainty_calibration/metrics.py#L32) | `raise ValueError('Abstention confidence threshold must be at least .5')` | Construct the triggering input and explain why rejection preserves the contract. |
| [35](../../uncertainty_calibration/metrics.py#L35) | `raise ValueError('Evidence expiry must follow assessment time')` | Construct the triggering input and explain why rejection preserves the contract. |
| [40](../../uncertainty_calibration/metrics.py#L40) | `raise ValueError('Each split requires 1 to 10000 rows')` | Construct the triggering input and explain why rejection preserves the contract. |
| [45](../../uncertainty_calibration/metrics.py#L45) | `raise ValueError('Unique nonempty row IDs across splits required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [49](../../uncertainty_calibration/metrics.py#L49) | `raise ValueError('Binary integer outcomes required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [52](../../uncertainty_calibration/metrics.py#L52) | `def reliability(rows, bins):` | State the input/output contract and trace one normal and one failing case. |
| [66](../../uncertainty_calibration/metrics.py#L66) | `return result, ece` | Predict the returned value and distinguish a computed result from authorization. |
| [69](../../uncertainty_calibration/metrics.py#L69) | `def evaluate(data):` | State the input/output contract and trace one normal and one failing case. |
| [94](../../uncertainty_calibration/metrics.py#L94) | `return {'schema_version': 1, 'label': data['label'],` | Separate type, shape and value checks; test a missing field and an invalid value. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_calibration.py](../../tests/test_calibration.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. Conformal coverage assumptions and descriptive metrics do not establish population calibration; TDA has no demonstrated necessity here.
