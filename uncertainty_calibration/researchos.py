"""Domain adapter for the pinned canonical ResearchOS controller."""
import base64
import hashlib

from ._tect.core import canonical, policy_default, replay


def scenario(data, metrics):
    summary = {k: metrics[k] for k in ('counts', 'brier_score', 'log_loss', 'log_loss_status',
                                      'expected_calibration_error', 'population_calibration_established')}
    payload = {'domain': 'binary-uncertainty-calibration',
               'input_sha256': hashlib.sha256(canonical(data).encode()).hexdigest(),
               'metrics_sha256': hashlib.sha256(canonical(metrics).encode()).hexdigest(),
               'summary': summary,
               'scope': 'Local computation from supplied outcomes; not independent scientific validation'}
    content = canonical(payload).encode()
    operations = [
        {'op': 'register', 'actor': 'author', 'data': {
            'id': 'calibration-study', 'statement': 'Compute bounded binary uncertainty metrics from the captured input',
            'provenance': ['local:input.json', 'local:uncertainty_calibration.metrics'],
            'confidence': .5, 'assurance_scope': 'Offline finite computation only'}},
        {'op': 'transition', 'actor': 'validator', 'data': {'claim': 'calibration-study', 'target': 'UNVERIFIED'}},
        {'op': 'evidence', 'actor': 'validator', 'data': {
            'id': 'computed-metrics', 'claim': 'calibration-study', 'claim_version': 1,
            'kind': 'validation', 'result': 'PASS', 'source': 'local:captured-input',
            'method': 'domain-adapter-v1', 'run_id': 'local-computation', 'group': 'same-local-process',
            'weight': 1, 'quality': 1, 'reliability': 1, 'independence': .5,
            'observed_at': data['as_of'], 'expires_at': data['expires_at'],
            'content_base64': base64.b64encode(content).decode(),
            'sha256': hashlib.sha256(content).hexdigest()}},
    ]
    for target in ('SUPPORTED', 'ADVERSARIAL_TEST', 'REPRODUCED'):
        operations.append({'op': 'transition', 'actor': 'validator',
                           'data': {'claim': 'calibration-study', 'target': target}})
    return {'schema_version': 1, 'as_of': data['as_of'], 'policy': policy_default(), 'operations': operations}


def assess(data, metrics):
    captured = scenario(data, metrics)
    controller = replay(captured)
    if any(e['outcome'] != 'PASS' for e in controller.ledger[:-1]):
        raise ValueError('Unexpected ResearchOS adapter failure')
    if controller.ledger[-1]['outcome'] != 'UNCERTAIN':
        raise ValueError('Missing external evidence must block reproduction')
    return captured, controller.ledger, controller.report()
