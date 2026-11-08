"""Exact, exclusive offline bundles. Replay is consistency, not authenticity."""
import hashlib
import html
import json
from pathlib import Path
import shutil

from ._tect.core import canonical
from ._tect.io import load
from .metrics import evaluate
from .researchos import assess


FILES = {'input.json', 'metrics.json', 'scenario.json', 'ledger.json',
         'researchos.json', 'review.html', 'manifest.json'}


def fingerprint():
    root = Path(__file__).parent
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*.py'))}


def contents(data):
    metrics = evaluate(data)
    scenario, ledger, report = assess(data, metrics)
    values = {name: canonical(value) for name, value in {
        'input.json': data, 'metrics.json': metrics, 'scenario.json': scenario,
        'ledger.json': ledger, 'researchos.json': report}.items()}
    rows = ''.join('<tr><td>' + '</td><td>'.join(html.escape(str(x)) for x in
                   (b['lower'], b['upper'], b['count'], b['mean_probability'], b['observed_frequency']))
                   + '</td></tr>' for b in metrics['reliability_bins'])
    values['review.html'] = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Binary uncertainty review</title><style>body{font:16px system-ui;max-width:960px;margin:40px auto;padding:16px}'
        'table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
        '<h1>Binary uncertainty review</h1><p>' + html.escape(data['label']) + '</p>'
        '<p>Local finite computation. Population calibration and independent reproduction are not established.</p>'
        '<h2>Reliability bins</h2><table><tr><th>Lower</th><th>Upper</th><th>Count</th><th>Mean probability</th><th>Observed frequency</th></tr>'
        + rows + '</table><h2>Metrics and limits</h2><pre>' + html.escape(json.dumps(metrics, indent=2))
        + '</pre><h2>ResearchOS assurance blockers</h2><pre>'
        + html.escape(json.dumps(report['assurance_blockers'], indent=2)) + '</pre></html>\n')
    values['manifest.json'] = canonical({'schema_version': 1, 'runtime': fingerprint(),
        'files': {name: hashlib.sha256(value.encode()).hexdigest() for name, value in values.items()}})
    if any(len(v.encode()) > 8*1024*1024 for v in values.values()):
        raise ValueError('Bundle file exceeds 8 MiB limit')
    return values


def write(data, output):
    values = contents(data)
    output = Path(output)
    output.mkdir()  # Existing results are never replaced.
    try:
        for name, value in values.items():
            (output/name).write_text(value, encoding='utf-8')
    except BaseException:
        shutil.rmtree(output)
        raise
    return json.loads(values['researchos.json'])


def verify(output):
    output = Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != FILES:
        raise ValueError('Invalid bundle file set')
    for name in FILES:
        path = output/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 8*1024*1024:
            raise ValueError('Expected bounded regular bundle files')
    expected = contents(load(output/'input.json'))
    for name, value in expected.items():
        if (output/name).read_bytes() != value.encode():
            raise ValueError('Recomputation mismatch: ' + name)
    return json.loads(expected['researchos.json'])
