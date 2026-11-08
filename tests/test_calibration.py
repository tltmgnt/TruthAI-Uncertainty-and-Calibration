import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

from uncertainty_calibration.metrics import evaluate
from uncertainty_calibration.bundle import write, verify
from uncertainty_calibration.researchos import assess
from uncertainty_calibration._tect.core import replay
from uncertainty_calibration._tect.io import load

ROOT = Path(__file__).resolve().parents[1]


def sample():
    return json.loads((ROOT/'examples/binary.json').read_text())


class CalibrationTests(unittest.TestCase):
    def test_hand_computed_scores(self):
        data = sample()
        report = evaluate(data)
        self.assertAlmostEqual(report['brier_score'], .225)
        self.assertAlmostEqual(report['log_loss'], -(math.log(.8)+math.log(.9)+math.log(.3)+math.log(.4))/4)
        self.assertAlmostEqual(report['expected_calibration_error'], .4)
        self.assertEqual(report['accuracy'], .5)
        self.assertEqual(report['abstention']['coverage'], .5)
        self.assertEqual(report['abstention']['selective_accuracy'], 1)
        self.assertFalse(report['population_calibration_established'])

    def test_endpoints_infinite_loss_and_empty_abstention(self):
        data = sample()
        data['evaluation'] = [{'id':'z', 'probability':0, 'outcome':1}]
        report = evaluate(data)
        self.assertIsNone(report['log_loss'])
        self.assertEqual(report['log_loss_status'], 'positive_infinity')
        self.assertEqual(report['brier_score'], 1)
        data['evaluation'][0].update(probability=.5)
        report = evaluate(data)
        self.assertEqual(report['abstention']['accepted'], 0)
        self.assertIsNone(report['abstention']['selective_accuracy'])
        data['evaluation'][0].update(probability=1, outcome=1)
        report = evaluate(data)
        self.assertEqual(report['log_loss'], 0)
        self.assertEqual(report['reliability_bins'][-1]['count'], 1)

    def test_conformal_quantile_and_unbounded_small_sample(self):
        data = sample()
        report = evaluate(data)['conformal']
        self.assertAlmostEqual(report['threshold'], .4)
        self.assertEqual(report['rank'], 4)
        self.assertEqual([s['labels'] for s in report['prediction_sets']], [[0], [1], [1], [0]])
        self.assertEqual(report['empirical_coverage'], .5)
        data['alpha'] = .01
        report = evaluate(data)['conformal']
        self.assertEqual(report['threshold_status'], 'unbounded')
        self.assertTrue(all(s['labels'] == [0, 1] for s in report['prediction_sets']))
        data['calibration'] = [{'id':f'c{i}', 'probability':.2, 'outcome':0} for i in range(9)]
        data['alpha'] = .7
        self.assertEqual(evaluate(data)['conformal']['rank'], 3)

    def test_perfect_predictions_and_shift(self):
        data = sample()
        data['evaluation'] = [{'id':'x','probability':0,'outcome':0},
                              {'id':'y','probability':1,'outcome':1}]
        report = evaluate(data)
        self.assertEqual(report['brier_score'], 0)
        self.assertEqual(report['log_loss'], 0)
        self.assertEqual(report['expected_calibration_error'], 0)
        self.assertGreaterEqual(report['shift']['probability_histogram_total_variation'], 0)

    def test_bad_inputs(self):
        for key, value in [('alpha',0), ('alpha',1), ('bins',True), ('bins',1),
                           ('abstention_threshold',.2), ('evaluation',[]), ('label',''),
                           ('schema_version',True), ('expires_at','2026-01-01T00:00:00Z')]:
            data = sample(); data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError): evaluate(data)
        for value in (True, float('nan'), float('inf'), -.1, 1.1):
            data = sample(); data['evaluation'][0]['probability'] = value
            with self.assertRaises(ValueError): evaluate(data)
        data = sample(); data['evaluation'][0]['id'] = 'c1'
        with self.assertRaises(ValueError): evaluate(data)
        data = sample(); data['evaluation'][0]['outcome'] = True
        with self.assertRaises(ValueError): evaluate(data)
        data = sample(); data['unknown'] = 1
        with self.assertRaises(ValueError): evaluate(data)

    def test_researchos_blocks_missing_reproduction(self):
        data = sample(); metrics = evaluate(data)
        scenario, ledger, report = assess(data, metrics)
        self.assertEqual(ledger[-1]['outcome'], 'UNCERTAIN')
        self.assertIn('SEPARATE_REPRODUCTION_MISSING', ledger[-1]['reasons'])
        self.assertFalse(report['execution_authorized'])
        self.assertEqual(report['state']['claims']['calibration-study']['state'], 'ADVERSARIAL_TEST')
        controller = replay(scenario)
        event = controller.apply({'op':'revise','actor':'author','data':{
            'claim':'calibration-study','statement':'Changed predictor or dataset',
            'confidence':.5,'provenance':['new-input'],'assurance_scope':'Offline only'}})
        self.assertEqual(event['outcome'],'PASS')
        self.assertEqual(controller.snapshot()['claims']['calibration-study']['state'], 'UNVERIFIED')
        self.assertIn('REQUIRED_VALIDATION_NOT_PASSED:domain-adapter-v1',
                      controller.report()['assurance_blockers']['calibration-study'])

    def test_integrity_expiry_and_actor_probes(self):
        data = sample(); scenario, _, _ = assess(data, evaluate(data))
        for modification in ('digest','expiry','actor'):
            bad = copy.deepcopy(scenario)
            evidence = bad['operations'][2]
            if modification == 'digest': evidence['data']['sha256'] = '0'*64
            if modification == 'expiry': evidence['data']['expires_at'] = data['as_of']
            if modification == 'actor': evidence['actor'] = 'author'
            c = replay(bad)
            self.assertEqual(c.ledger[2]['outcome'], 'FAIL')
            self.assertNotEqual(c.snapshot()['claims']['calibration-study']['state'], 'ASSURED')

    def test_recompute_bundle_and_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'run'
            write(sample(), output)
            self.assertEqual(verify(output)['engine_version'], '0.1.0')
            with self.assertRaises(FileExistsError): write(sample(), output)
            (output/'metrics.json').write_text('{}')
            # Rehashing a forged manifest cannot make changed metrics pass replay.
            manifest = json.loads((output/'manifest.json').read_text())
            manifest['files']['metrics.json'] = hashlib.sha256(b'{}').hexdigest()
            (output/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError): verify(output)

    def test_html_escaping_and_strict_json(self):
        from uncertainty_calibration.bundle import contents
        data = sample(); data['label'] = '<script>alert(1)</script>'
        self.assertNotIn('<script>', contents(data)['review.html'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bad.json'
            path.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): load(path)
            path.write_text('{"a":1e999}')
            with self.assertRaises(ValueError): load(path)

    def test_canonical_core_hashes(self):
        lock = json.loads((ROOT/'researchos-lock.json').read_text())
        for filename, expected in lock['release']['modules'].items():
            path = ROOT/'uncertainty_calibration/_tect'/filename
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, filename)


if __name__ == '__main__':
    unittest.main()
