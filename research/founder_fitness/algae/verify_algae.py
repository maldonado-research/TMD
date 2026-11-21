#!/usr/bin/env python3
"""Recompute aggregate Bestion et al. green-algae comparisons using Python 3."""
import argparse
import csv
import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

GROWTH_MD5 = 'afc8b00678c0f107840ac80e6c474fb5'
COMPETITION_MD5 = '2cefeaabfb4ae74bab41d4c8294a9cc4'
DAYS = (5, 14, 23)
CLASSIFIERS = ('lda', 'randomforest', 'rpart')


def read_rows(path, expected):
    if hashlib.md5(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Unexpected archive checksum for {path}')
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def load_rates(growth):
    rates = defaultdict(list)
    for row in growth:
        if row['SpeciesNb'] != '6':
            key = (row['SpeciesNb'], float(row['Temperature_c']), float(row['Phosphate_c']))
            rates[key].append(float(row['mu']))
    return {key: mean(values) for key, values in rates.items()}


def extract(competition, rates, day, classifier):
    counts = Counter()
    groups = defaultdict(list)
    for row in competition:
        if int(row['Day']) != day:
            continue
        counts['archive_rows'] += 1
        if '6' in (row['SpeciesA'], row['SpeciesB']):
            counts['species_scope_excluded'] += 1
            continue
        counts['in_scope'] += 1
        if row['Samples_to_remove_low_density'] != '0':
            counts['low_density_excluded'] += 1
            continue
        env = (float(row['Temperature_fact'][1:]), float(row['Phosphate_fact'][1:]))
        key_a, key_b = (row['SpeciesA'], *env), (row['SpeciesB'], *env)
        if key_a not in rates or key_b not in rates:
            counts['missing_rate_excluded'] += 1
            continue
        a = float(row[f'nb_cells_SpA_{classifier}'])
        b = float(row[f'nb_cells_SpB_{classifier}'])
        assert math.isfinite(a + b) and a + b > 0
        actual = a / (a + b)
        delta = math.log(10) * (rates[key_a] - rates[key_b])
        predicted = 1 / (1 + math.exp(-day * delta))
        groups[(row['Species_pair'], env)].append((predicted, actual))
        counts['scored_fraction'] += 1
        counts['observed_ties'] += a == b
        counts['predicted_ties'] += delta == 0
    return counts, groups


def agreement(observations):
    decisive = [(p, y) for p, y in observations if p != 0.5 and y != 0.5]
    return sum((p - 0.5) * (y - 0.5) > 0 for p, y in decisive), len(decisive)


def metrics(observations):
    wins, n = agreement(observations)
    return {'n': len(observations), 'correct': wins, 'decisive': n,
            'mae_rate': mean(abs(p - y) for p, y in observations),
            'mae_half': mean(abs(0.5 - y) for p, y in observations),
            'mse_rate': mean((p - y)**2 for p, y in observations),
            'mse_half': mean((0.5 - y)**2 for p, y in observations)}


def report(groups):
    flat = [obs for obs_group in groups.values() for obs in obs_group]
    summary = metrics(flat)
    pair_condition_rates = defaultdict(list)
    pair_condition_errors = defaultdict(list)
    observed_means, observed_medians = [], []
    for (pair, env), group in groups.items():
        p = group[0][0]
        assert all(pred == p for pred, _ in group)
        observed_means.append((p, mean(actual for _, actual in group)))
        observed_medians.append((p, median(actual for _, actual in group)))
        g = metrics(group)
        if g['decisive']:
            pair_condition_rates[pair].append(g['correct'] / g['decisive'])
        pair_condition_errors[pair].append(g['mae_rate'] - g['mae_half'])
    wins_mean, n_mean = agreement(observed_means)
    wins_median, n_median = agreement(observed_medians)
    per_pair_accuracy = [mean(vals) for vals in pair_condition_rates.values()]
    per_pair_error = [mean(vals) for vals in pair_condition_errors.values()]
    return {**summary, 'pairs': len(pair_condition_errors), 'pair_conditions': len(groups),
            'mean_share_correct': wins_mean, 'mean_share_decisive': n_mean,
            'median_share_correct': wins_median, 'median_share_decisive': n_median,
            'balanced_accuracy_pairs_conditions': mean(per_pair_accuracy),
            'balanced_mae_rate_minus_half': mean(per_pair_error),
            'omit_one_pair_balanced_accuracy_min': min(mean(per_pair_accuracy[:i] + per_pair_accuracy[i+1:]) for i in range(len(per_pair_accuracy))),
            'omit_one_pair_balanced_accuracy_max': max(mean(per_pair_accuracy[:i] + per_pair_accuracy[i+1:]) for i in range(len(per_pair_accuracy)))}


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: round(value, 8) if isinstance(value, float) else value for key, value in row.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('growth_csv', type=Path)
    parser.add_argument('competition_csv', type=Path)
    parser.add_argument('--out-dir', type=Path, default=Path('.'))
    args = parser.parse_args()
    growth = read_rows(args.growth_csv, GROWTH_MD5)
    competition = read_rows(args.competition_csv, COMPETITION_MD5)
    assert (len(growth), len(competition)) == (938, 1620)
    assert len({(r['Day'], r['Species_pair'], r['Temperature_fact'], r['Phosphate_fact'], r['Replicate']) for r in competition}) == len(competition)
    assert len({(r['SpeciesNb'], r['Temperature_c'], r['Phosphate_c'], r['Replicate']) for r in growth}) == len(growth)
    rates = load_rates(growth)
    summary, attrition = [], []
    for day in DAYS:
        for classifier in CLASSIFIERS if day == 23 else ('lda',):
            counts, groups = extract(competition, rates, day, classifier)
            if classifier == 'lda':
                assert counts['in_scope'] == counts['low_density_excluded'] + counts['missing_rate_excluded'] + counts['scored_fraction']
                attrition.append({'day': day, **counts})
            summary.append({'day': day, 'classifier': classifier, **report(groups)})
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / 'algae_attrition.csv', attrition)
    write_csv(args.out_dir / 'algae_validation.csv', summary)


if __name__ == '__main__':
    main()
