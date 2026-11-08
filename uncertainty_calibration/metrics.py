"""Descriptive binary scores and split-conformal prediction sets.

No fitted recalibrator, causal claim, or population coverage certification.
"""
import math
from fractions import Fraction


def fields(obj, names):
    if type(obj) is not dict or set(obj) != set(names):
        raise ValueError('Missing or unknown fields')


def probability(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Finite probability in [0,1] required')
    return value


def validate(data):
    fields(data, ('schema_version', 'label', 'calibration', 'evaluation', 'bins',
                  'alpha', 'abstention_threshold', 'as_of', 'expires_at'))
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported schema version')
    if type(data['label']) is not str or not data['label'].strip() or len(data['label']) > 200:
        raise ValueError('Short nonempty dataset label required')
    if type(data['bins']) is not int or not 2 <= data['bins'] <= 50:
        raise ValueError('Between 2 and 50 bins required')
    if not 0 < probability(data['alpha']) < 1:
        raise ValueError('alpha must be strictly between zero and one')
    if not .5 <= probability(data['abstention_threshold']) <= 1:
        raise ValueError('Abstention confidence threshold must be at least .5')
    from ._tect.core import date
    if date(data['as_of']) >= date(data['expires_at']):
        raise ValueError('Evidence expiry must follow assessment time')
    seen = set()
    for split in ('calibration', 'evaluation'):
        rows = data[split]
        if type(rows) is not list or not 1 <= len(rows) <= 10000:
            raise ValueError('Each split requires 1 to 10000 rows')
        for row in rows:
            fields(row, ('id', 'probability', 'outcome'))
            identifier = row['id']
            if type(identifier) is not str or not identifier.strip() or len(identifier) > 200 or identifier in seen:
                raise ValueError('Unique nonempty row IDs across splits required')
            seen.add(identifier)
            probability(row['probability'])
            if type(row['outcome']) is not int or row['outcome'] not in (0, 1):
                raise ValueError('Binary integer outcomes required')


def reliability(rows, bins):
    groups = [[] for _ in range(bins)]
    for row in rows:
        groups[min(bins - 1, int(row['probability'] * bins))].append(row)
    result, ece = [], 0.0
    for index, group in enumerate(groups):
        n = len(group)
        predicted = sum(r['probability'] for r in group) / n if n else None
        observed = sum(r['outcome'] for r in group) / n if n else None
        if n:
            ece += n / len(rows) * abs(predicted - observed)
        result.append({'lower': index / bins, 'upper': (index + 1) / bins,
                       'right_inclusive': index == bins - 1, 'count': n,
                       'mean_probability': predicted, 'observed_frequency': observed})
    return result, ece


def evaluate(data):
    validate(data)
    rows, calibration = data['evaluation'], data['calibration']
    n = len(rows)
    bins, ece = reliability(rows, data['bins'])
    impossible = sum(r['probability'] == 0 and r['outcome'] == 1 or
                     r['probability'] == 1 and r['outcome'] == 0 for r in rows)
    losses = [-math.log(r['probability']) if r['outcome'] else -math.log1p(-r['probability'])
              for r in rows if not (r['probability'] == 0 and r['outcome'] == 1 or
                                    r['probability'] == 1 and r['outcome'] == 0)]
    accepted = [r for r in rows if max(r['probability'], 1-r['probability']) >= data['abstention_threshold']]
    accuracy = lambda items: sum((r['probability'] >= .5) == bool(r['outcome']) for r in items) / len(items) if items else None
    # Binary nonconformity is 1 minus probability assigned to the true class.
    scores = sorted(1-r['probability'] if r['outcome'] else r['probability'] for r in calibration)
    # Decimal input semantics avoid an extra rank from float roundoff at integers.
    rank = math.ceil((len(scores) + 1) * (1-Fraction(str(data['alpha']))))
    unbounded = rank > len(scores)
    threshold = None if unbounded else scores[rank-1]
    prediction_sets = []
    for r in rows:
        labels = [y for y, score in ((0, r['probability']), (1, 1-r['probability']))
                  if unbounded or score <= threshold]
        prediction_sets.append({'id': r['id'], 'labels': labels, 'covered': r['outcome'] in labels})
    old_bins, _ = reliability(calibration, data['bins'])
    tv = .5 * sum(abs(a['count']/len(calibration) - b['count']/n) for a, b in zip(old_bins, bins))
    return {'schema_version': 1, 'label': data['label'],
            'counts': {'calibration': len(calibration), 'evaluation': n},
            'brier_score': sum((r['probability']-r['outcome'])**2 for r in rows)/n,
            'log_loss': None if impossible else sum(losses)/n,
            'log_loss_status': 'positive_infinity' if impossible else 'finite',
            'impossible_outcome_count': impossible,
            'reliability_bins': bins, 'expected_calibration_error': ece,
            'accuracy': accuracy(rows),
            'abstention': {'threshold': data['abstention_threshold'], 'accepted': len(accepted),
                           'coverage': len(accepted)/n, 'selective_accuracy': accuracy(accepted)},
            'conformal': {'alpha': data['alpha'], 'rank': rank, 'threshold': threshold,
                          'threshold_status': 'unbounded' if unbounded else 'finite',
                          'prediction_sets': prediction_sets,
                          'empirical_coverage': sum(s['covered'] for s in prediction_sets)/n,
                          'mean_set_size': sum(len(s['labels']) for s in prediction_sets)/n},
            'shift': {'probability_histogram_total_variation': tv,
                      'status': 'descriptive_not_a_significance_test'},
            'population_calibration_established': False,
            'limitations': ['Descriptive finite sample metrics; ECE depends on binning',
                           'Conformal marginal coverage requires exchangeable calibration/test scores and a fixed predictor',
                           'Disjoint IDs do not establish independent samples or prevent training leakage',
                           'Histogram distance does not establish exchangeability or detect all distribution shifts',
                           'No fitted calibration transform or operational authorization']}
