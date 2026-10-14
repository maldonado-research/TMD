#!/usr/bin/env python3
"""Original, read-only Python reproduction of the deposited Figure 2D summary.

Reads authenticated public archive members into memory. It never executes the
authors' R/Rmarkdown/HTML code or writes/extracts source files. MIT licensed.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import tarfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
CONTROLS = ['Cn4001', 'Cn5001', 'Cn5002', 'Cn6001', 'Sc4001', 'Sc5003',
            'Sc5004', 'Sc5005', 'Sc5006', 'Sc6001', 'Sc5001', 'Sc5002']
COLUMNS = ['srr_accession', 'primer_id', 'level_id'] + CONTROLS + ['environmental']

def require(ok, label):
    if not ok:
        raise ValueError(label)

def read_members(cache, provenance):
    output = {}
    for archive in provenance['original_archives']:
        path = cache / archive['filename']
        require(path.is_file() and not path.is_symlink(), 'Regular archive: ' + path.name)
        blob = path.read_bytes()
        require(len(blob) == archive['bytes'] and
                hashlib.sha256(blob).hexdigest() == archive['sha256'] and
                hashlib.md5(blob).hexdigest() == archive['advertised_md5'],
                'Authenticated archive: ' + path.name)
        wanted = [m for m in provenance['selected_members'] if m['archive'] == path.name]
        with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
            members = tar.getmembers()
            require(len(members) <= 250, 'Bounded archive member count')
            names = [m.name for m in members]
            require(len(names) == len(set(names)), 'Unique archive member names')
            for m in members:
                p = PurePosixPath(m.name)
                require(not p.is_absolute() and '..' not in p.parts and '\\' not in m.name,
                        'Safe archive path')
                require(m.isfile() or m.isdir(), 'No archive links/devices')
                require(not getattr(m, 'sparse', None), 'No sparse members')
            require(sum(m.size for m in members if m.isfile()) <= 24 * 1024 * 1024,
                    'Bounded expanded archive')
            for item in wanted:
                member = tar.getmember(item['path'])
                require(member.isfile() and member.size == item['bytes'] <= 1024 * 1024,
                        'Bounded selected regular member')
                data = tar.extractfile(member).read()
                require(hashlib.sha256(data).hexdigest() == item['sha256'],
                        'Selected member identity: ' + item['path'])
                output[item['path']] = data
    return output

class PreText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inside = False
        self.current = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.inside = True
            self.current = []

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.blocks.append(''.join(self.current))
            self.inside = False

    def handle_data(self, text):
        if self.inside:
            self.current.append(text)

def author_output(blob):
    parser = PreText()
    parser.feed(blob.decode('utf-8'))
    candidates = [x for x in parser.blocks if '##   primer_id     slope r.squared' in x]
    require(len(candidates) == 1, 'Unique archived author summary table')
    result = {}
    for primer, slope, r2 in re.findall(r'^##\s+\d+\s+(ITS1|ITS2|V4)\s+([0-9.]+)\s+([0-9.]+)\s*$', candidates[0], re.M):
        require(primer not in result, 'Unique author primer summary')
        result[primer] = {'slope': float(slope), 'r_squared': float(r2)}
    require(set(result) == {'ITS1', 'ITS2', 'V4'}, 'Three archived author fits')
    return result

def transform(blob):
    reader = csv.DictReader(io.StringIO(blob.decode('utf-8')), delimiter='\t')
    require(reader.fieldnames == COLUMNS, 'Exact Figure 2D schema')
    require([c for c in COLUMNS[3:] if '00' in c] == CONTROLS,
            'Explicit controls agree with author name rule')
    points = []
    seen = set()
    for row in reader:
        accession = row['srr_accession']
        require(re.fullmatch(r'SRR[0-9]+', accession) and accession not in seen,
                'Unique public accession')
        seen.add(accession)
        primer = row['primer_id']
        require(primer in ('ITS1', 'ITS2', 'V4'), 'Known primer')
        soil = int(row['level_id'])
        require(soil in (37, 75, 150, 300), 'Source soil level in mg')
        counts = {k: int(row[k]) for k in CONTROLS + ['environmental']}
        require(all(n >= 0 for n in counts.values()), 'Nonnegative integer read counts')
        control = sum(counts[k] for k in CONTROLS)
        environmental = counts['environmental']
        require(control > 0 and environmental > 0, 'Positive aggregate numerator/denominator')
        if primer == 'V4':
            require(all(counts[k] == 0 for k in CONTROLS if k not in ('Sc5001', 'Sc5002')),
                    'V4 incompatible-standard columns are structural zero')
        points.append({'accession': accession, 'primer': primer, 'soil_mg': soil,
                       'log10_soil_mg': math.log10(soil),
                       'log10_environmental_over_controls': math.log10(environmental / control)})
    require(len(points) == 22, 'All 22 processed input rows')
    return points

def fit(points):
    x = [r['log10_soil_mg'] for r in points]
    y = [r['log10_environmental_over_controls'] for r in points]
    n = len(x)
    xbar, ybar = math.fsum(x) / n, math.fsum(y) / n
    dx, dy = [v - xbar for v in x], [v - ybar for v in y]
    sxx = math.fsum(v * v for v in dx)
    sxy = math.fsum(a * b for a, b in zip(dx, dy))
    slope = sxy / sxx
    intercept = ybar - slope * xbar
    sse = math.fsum((b - intercept - slope * a) ** 2 for a, b in zip(x, y))
    sst = math.fsum(v * v for v in dy)
    return {'n_accession_rows': n, 'soil_levels_mg': sorted(set(r['soil_mg'] for r in points)),
            'rows_per_soil_level': {str(k): v for k, v in sorted(Counter(r['soil_mg'] for r in points).items())},
            'slope': slope, 'intercept': intercept, 'r_squared': 1 - sse / sst,
            'residual_sum_of_squares': sse, 'total_sum_of_squares': sst}

def replay(cache, provenance):
    members = read_members(cache, provenance)
    rmd = members['rmarkdowns/figure2D.Rmd'].decode('utf-8')
    for anchor in provenance['recipe_text_anchors']:
        require(anchor in rmd, 'Archived recipe anchor')
    points = transform(members['data/figure2D.tsv'])
    archived = author_output(members['rmarkdowns/figure2D.html'])
    fits = {}
    for primer in ('ITS1', 'ITS2', 'V4'):
        selected = [p for p in points if p['primer'] == primer]
        fits[primer] = fit(selected)
        expect_n = 6 if primer == 'V4' else 8
        require(len(selected) == expect_n and all(v == 2 for v in fits[primer]['rows_per_soil_level'].values()),
                'Two accession rows per included mass')
        fits[primer]['archived_author_display'] = archived[primer]
        fits[primer]['author_display_agreement_absolute_tolerance'] = 5e-8
        for name in ('slope', 'r_squared'):
            require(abs(fits[primer][name] - archived[primer][name]) <= 5e-8,
                    'Agreement with author displayed precision: ' + primer + '/' + name)
        fits[primer]['two_decimal_label'] = f"{fits[primer]['slope']:.2f} ({fits[primer]['r_squared']:.2f})"
    output = {'status': 'PASS_PROCESSED_FIGURE2D_DESCRIPTIVE_REPLAY',
              'figure': '2D', 'fallback_used': False, 'processed_accession_rows': len(points),
              'fit_method': 'Unweighted OLS with intercept by primer; all supplied rows retained.',
              'predictor': 'log10(nominal soil amount in mg)',
              'response': 'log10(environmental reads / sum of all twelve rDNA-mimic count columns)',
              'pseudocount': None, 'new_exclusions': 0, 'source_author_code_executed': False,
              'independent_biological_unit_count': None, 'inferential_confidence_intervals': None,
              'absolute_spike_copy_truth_verified': False, 'native_TMD_parameters_estimated': False,
              'fits': fits}
    return output, points

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path, required=True)
    args = parser.parse_args()
    provenance = json.loads((HERE / 'SOURCE_PROVENANCE.json').read_text())
    result, _ = replay(args.source_cache, provenance)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
