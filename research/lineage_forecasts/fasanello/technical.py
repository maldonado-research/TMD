"""Score the original and repeated measurements on the same Fasanello wells."""
import argparse
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path

COUNTS_SHA256 = '619c7d99a261304a5117fa24530573a2dabc2f7deca0aea812a1c2ce00a522bb'
LIBRARIES = ('original', 'rerun')
RULES = ('baseline', 'early', 'change')


def read_counts(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != COUNTS_SHA256:
        raise ValueError('The technical repeat table differs from the release copy')
    populations = {}
    with path.open(encoding='utf-8', newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            visits = populations.setdefault(row['population_id'], {})
            day = int(row['day'])
            if day in visits:
                raise ValueError('Duplicate population visit')
            sample = {}
            for lib in LIBRARIES:
                a, b = row[f'{lib}_A'], row[f'{lib}_B']
                if bool(a) != bool(b):
                    raise ValueError('Both counts are required for an observed sample')
                if a:
                    sample[lib] = (int(a), int(b))
                    if min(sample[lib]) < 0:
                        raise ValueError('Negative count')
            sample['selected'] = sample[row['selected']]
            visits[day] = sample
    return populations


def leader(score, eligible):
    scores = (score, 1 - score)
    maximum = max(scores[i] for i in eligible)
    leaders = [i for i in eligible if scores[i] == maximum]
    return leaders[0] if len(leaders) == 1 else None


def calls(visits, library):
    counts = [visits.get(day, {}).get(library) for day in (0, 10, 25)]
    if any(pair is None or sum(pair) == 0 for pair in counts):
        return None
    base, early, final = counts
    p0, pe, pf = [Fraction(a, a+b) for a, b in counts]
    base_labels = [i for i in (0, 1) if base[i] > 0]
    early_labels = [i for i in (0, 1) if base[i] + early[i] > 0]
    return {'baseline': leader(p0, base_labels), 'early': leader(pe, early_labels),
            'change': leader(2*pe-p0, early_labels), 'final': leader(pf, (0, 1))}


def score(records, prediction, target):
    hits = dict.fromkeys(RULES, 0)
    abstentions = dict.fromkeys(RULES, 0)
    endpoint_ties = early_only = change_only = 0
    for record in records:
        issued, outcome = record[prediction], record[target]['final']
        endpoint_ties += outcome is None
        correct = {}
        for rule in RULES:
            correct[rule] = outcome is not None and issued[rule] == outcome
            hits[rule] += correct[rule]
            abstentions[rule] += issued[rule] is None
        early_only += correct['early'] and not correct['change']
        change_only += correct['change'] and not correct['early']
    return {'predictions': prediction, 'endpoint': target, 'populations': len(records),
            'strict_hits': hits, 'early_only': early_only, 'change_only': change_only,
            'prediction_ties': abstentions, 'endpoint_ties': endpoint_ties}


def summarize(populations):
    libraries = (*LIBRARIES, 'selected')
    records = [{lib: calls(visits, lib) for lib in libraries} for visits in populations.values()]
    common = [r for r in records if all(r[lib] is not None for lib in LIBRARIES)]
    same = {k: sum(r['original'][k] == r['rerun'][k] and r['original'][k] is not None
                   for r in common) for k in (*RULES, 'final')}
    return {'population_roster': len(records), 'complete_in_both': len(common),
            'agreement_in_both': same,
            'within_library_all_available': [score([r for r in records if r[lib] is not None], lib, lib)
                                             for lib in libraries],
            'matched_population_comparisons': [score(common, x, y) for x in LIBRARIES for y in LIBRARIES]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('counts', type=Path, nargs='?',
                        default=Path(__file__).with_name('technical_counts.tsv'))
    print(json.dumps(summarize(read_counts(parser.parse_args().counts)), indent=2))
