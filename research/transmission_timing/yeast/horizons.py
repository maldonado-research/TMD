"""Compare the first high-frequency group when the follow-up ends at different visits."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
VISITS = (70, 1410, 2640, 5150, 7530, 10150)


def first_retained(groups, end, confirm):
    """First qualifying member of each group, given only visits up to end inclusive."""
    first = defaultdict(set)
    for group, rows in groups.items():
        candidates = []
        for row in rows:
            mask = row[:end+1]
            for i, state in enumerate(mask):
                if state != '2':
                    continue
                after = mask[i+1:]
                if '0' in after or '1' in after:
                    continue
                if confirm and '2' not in after:
                    continue
                candidates.append(i)
                break
        if candidates:
            first[min(candidates)].add(group)
    if not first:
        return None, set()
    i = min(first)
    return i, first[i]


def relation(a,b):
    if not a and not b:
        return 'neither_observed'
    if not a:
        return 'first_appears_later'
    if not b:
        return 'no_longer_any_qualifying_group'
    if a == b:
        return 'identical'
    return 'partly_overlapping' if a & b else 'disjoint'


def compare(populations, first_end, last_end, first_confirm=False, last_confirm=False):
    sizes, dates = Counter(), Counter()
    examples = {}
    for well, groups in sorted(populations.items()):
        i,a = first_retained(groups, first_end, first_confirm)
        j,b = first_retained(groups, last_end, last_confirm)
        status=relation(a,b)
        sizes[status] += 1
        if i is not None and j is not None:
            dates['later' if i < j else 'earlier' if i > j else 'same'] += 1
            # Extending follow-up or requiring confirmation can only remove a
            # member's qualifying start or move it to a later visit.
            assert j >= i
        examples[well] = [None if i is None else VISITS[i], None if j is None else VISITS[j],
                          len(a),len(b),len(a & b),status]
    return {'group_set_relations':dict(sorted(sizes.items())),
            'direction_of_first_qualifying_visit_when_both_observed':dict(sorted(dates.items())),
            'per_well_start_and_set_sizes':examples}


def summarize(wells):
    last=len(VISITS)-1
    prefixes={}
    for end in range(last):
        result=compare(wells, end, last)
        prefixes[str(VISITS[end])]={k:v for k,v in result.items()
                                     if k!='per_well_start_and_set_sizes'}
    return {'prefixes_compared_with_final':prefixes,
            'penultimate_vs_final':compare(wells,last-1,last),
            'final_requiring_second_adequately_covered_high_visit':compare(wells,last,last,False,True)}


def main():
    wells=defaultdict(lambda:defaultdict(list))
    with (HERE/'yeast_observations.tsv').open() as f:
        for row in csv.DictReader(f,delimiter='\t'):
            wells[row['well']][row['group']].append(row['visits'])
    assert len(wells)==18 and sum(len(g) for g in wells.values())==5543
    result={'visits':VISITS,'all_initially_haploid':summarize(wells),
            'excluding_P1B03':summarize({k:v for k,v in wells.items() if k!='P1B03'})}
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
