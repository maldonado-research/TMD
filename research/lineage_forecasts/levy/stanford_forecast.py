"""Score the frozen abundance forecast on the published Stanford teaching roster."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def load_counts(path):
    with path.open() as source:
        rows = csv.DictReader(source, skipinitialspace=True)
        header = rows.fieldnames
        assert header == ['Barcode ID'] + [f'Reads at t={t}' for t in (0, 16, 32, 40, 48, 64, 72, 80, 88, 96, 104, 112)]
        labels = []
        counts = [[], [], []]
        for row in rows:
            assert None not in row and all(row.values())
            labels.append(int(row['Barcode ID']))
            for j, t in enumerate((0, 16, 112)):
                x = int(row[f'Reads at t={t}'])
                assert x >= 0
                counts[j].append(x)
    assert len(set(labels)) == len(labels)
    return labels, counts


def ranked(values, focal):
    lower_rank = 1 + sum(value > focal for value in values)
    tied = sum(value == focal for value in values)
    return [lower_rank, lower_rank + tied - 1]


def predict(labels, values, counts, denom):
    maximum = max(values)
    next_distinct = max(x for x in values if x < maximum)
    winners = [i for i, x in enumerate(values) if x == maximum]
    runners = [labels[i] for i, x in enumerate(values) if x == next_distinct]
    return {
        'leader_count': len(winners),
        'winners': [{'id': labels[i], 'assigned_reads_t0_t16_t112': [col[i] for col in counts],
                     'rank_t0_t16_t112': [ranked(col, col[i]) for col in counts]} for i in winners],
        'next_distinct_score_ids': runners,
        'top_score_num': maximum, 'next_distinct_score_num': next_distinct,
        'leader_margin_num': maximum - next_distinct if len(winners) == 1 else 0,
        'score_den': denom,
    }


def score(path):
    labels, counts = load_counts(path)
    baseline, early, endpoint = counts
    db, de, df = map(sum, counts)
    assert min(db, de, df) > 0
    masks = Counter(''.join('1' if v else '0' for v in row) for row in zip(*counts))
    trend = [2 * y * db - x * de for x, y in zip(baseline, early)]
    return {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_visit_units': 'generation', 'used_visits': [0, 16, 112],
        'all_unique_roster_rows': len(labels), 'all_rows_in_each_rule': len(labels),
        'positive_t0_t16_t112': [sum(v > 0 for v in col) for col in counts],
        'positive_at_either_prediction_visit': sum(x > 0 or y > 0 for x, y in zip(baseline, early)),
        'positive_at_both_prediction_visits': sum(x > 0 and y > 0 for x, y in zip(baseline, early)),
        'detection_patterns_t0_t16_t112': dict(sorted(masks.items())),
        'assigned_reads_t0_t16_t112': [db, de, df],
        'baseline_persistence': predict(labels, baseline, counts, db),
        'early_persistence': predict(labels, early, counts, de),
        'two_visit_linear_trend': predict(labels, trend, counts, db * de),
        'endpoint': predict(labels, endpoint, counts, df),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    print(json.dumps(score(parser.parse_args().csv), indent=2))
