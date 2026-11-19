"""Compare selected grapevine marker pairs in the original and additional Tempranillo samples."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
WORKBOOK_SHA = '135002ebe85ea2307238cf7d866e7b799fdf27968e1f628a67ed76c91fae1b60'


def het(call):
    if not re.fullmatch(r'[ACGT]:[ACGT]', call):
        raise ValueError(f'Unknown genotype {call!r}')
    return int(call[0] != call[2])


def extract(path):
    from openpyxl import load_workbook
    assert sha256(path.read_bytes()).hexdigest() == WORKBOOK_SHA
    wb = load_workbook(path, data_only=True, read_only=True)
    try:
        s1, s2, s3, s4, s5 = [list(sheet.values) for sheet in wb]
    finally:
        wb.close()
    core = list(s5[1][2:])
    wide = list(s3[1][2:])
    assert set(core) == {r[0] for r in s2[2:] if r[6] == 'Yes'}
    assert set(wide) == {r[0] for r in s2[2:] if r[5] == 'Yes'}
    assert len(core) == len(set(core)) == 56 and len(wide) == len(set(wide)) == 158
    samples = {r[0]: (r[12],r[8]) for r in s1[2:] if str(r[0]).startswith('Tempranillo-')}
    assert len(samples) == 185 and len(samples) == sum(int(r[1]) for r in s5[2:])
    earlier = {name for name, (_, use) in samples.items() if use != 'TG'}
    assert earlier == {r[0] for r in s4[2:]} and len(earlier) == 50
    ancestors = dict(zip(wide,s3[4][2:]))
    assert s3[4][0] == 'Ancestral TT' and all(v == '-' or het(v) == 0 for v in ancestors.values())
    assert all((ancestors[s] == '-' or ancestors[s] == a == b) for s,a,b in zip(wide,s3[2][2:],s3[3][2:]))
    profiles = {r[0]: dict(zip(core,r[2:])) for r in s5[2:]}
    prior_profiles = {r[0]: dict(zip(wide,r[2:])) for r in s3[5:]}
    # The same identifiers and genotypes are checked across five sheets of one workbook.
    method_counts = Counter()
    discrepancies = []
    s4_profiles = {r[0]:{} for r in s4[2:]}
    assayed = set()
    for col in range(2, len(s4[1]), 2):
        method, name = s4[1][col].split(' - ')
        method_2, name_2 = s4[1][col+1].split(' - ')
        name = name.strip()
        assert name == name_2.strip() and method == 'Illumina' and method_2 == 'Fluidigm'
        assert name not in assayed
        assayed.add(name)
        for row in s4[2:]:
            vine, gt = row[:2]
            assert samples[vine][0] == gt
            a,b = row[col:col+2]
            assert a == b
            template = profiles[gt][name]
            assert template == prior_profiles[gt][name]
            s4_profiles[vine][name] = a
            if sorted(a) != sorted(template):
                discrepancies.append({'vine':vine,'clone':gt,'marker':name,'s4_genotype':a,'s3_and_s5_genotype':template})
            method_counts['heterozygous' if het(a) else 'homozygous'] += 1
    assert assayed == set(core)
    for site in core:
        states = {':'.join(sorted(p[site].split(':'))) for p in profiles.values()}
        assert len(states) == 2 and {het(x) for x in states} == {0,1}
        if ancestors[site] != '-':
            assert ancestors[site] in states
    for site in wide:
        states = {':'.join(sorted(p[site].split(':'))) for p in prior_profiles.values()}
        assert len(states) == 2 and {het(x) for x in states} == {0,1}
        if ancestors[site] != '-':
            assert ancestors[site] in states
    first = Counter(samples[v][0] for v in earlier)
    other = Counter(gt for v,(gt,_) in samples.items() if v not in earlier)
    assert first == {r[0]:r[1] for r in s3[5:]}
    assert first+other == {r[0]:r[1] for r in s5[2:]}
    def bits(prof, cols):
        return {gt: ''.join(str(het(profile[name])) for name in cols) for gt,profile in prof.items()}
    return {'source_workbook_sha256':WORKBOOK_SHA,'paired_genotype_agreements':dict(method_counts),
            's4_vs_templates':discrepancies, 's4_profiles':bits(s4_profiles,core),
            'selection_counts':dict(sorted(first.items())), 'additional_counts':dict(sorted(other.items())),
            'ancestral_state_unresolved':[s for s in wide if ancestors[s]=='-'],
            'selection_markers':wide,'selection_profiles':bits(prior_profiles,wide),
            'panel_markers':core,'expanded_profiles':bits(profiles,core)}


def pairs(sites, profiles, names):
    cols = [tuple(int(profiles[gt][i]) for gt in names) for i in range(len(sites))]
    states = {}
    for (i,a),(j,b) in combinations(enumerate(cols),2):
        present = set(zip(a,b))
        if sum(a)==0 or sum(b)==0 or sum(a)==len(a) or sum(b)==len(b):
            relation = 'constant_marker'
        elif (1,1) not in present:
            relation = 'disjoint'
        elif (1,0) not in present and (0,1) not in present:
            relation = 'equal'
        elif (1,0) not in present:
            relation = 'first_within_second'
        elif (0,1) not in present:
            relation = 'second_within_first'
        else:
            relation = 'crossing'
        states[sites[i],sites[j]] = (len(present), relation)
    return states


def report(data):
    first, extra = data['selection_counts'], data['additional_counts']
    profiles = data['expanded_profiles']
    unknown = set(data['ancestral_state_unresolved'])
    core = data['panel_markers']
    def summarize(table):
        resolved = [r for (a,b),(_,r) in table.items() if a not in unknown and b not in unknown]
        return {'pairs':len(table),'all_four_observed':sum(k==4 for k,_ in table.values()),
                'ancestrally_resolved_pairs':len(resolved),'rooted_relations':dict(sorted(Counter(resolved).items()))}
    selection = pairs(core, profiles, sorted(first))
    additional = pairs(core, profiles, sorted(extra))
    combined = pairs(core, profiles, sorted(profiles))
    wide = pairs(data['selection_markers'], data['selection_profiles'], sorted(first))
    raw_selection = pairs(core, data['s4_profiles'], sorted(data['s4_profiles']))
    mixed_profiles = {**data['s4_profiles'], **{gt:profiles[gt] for gt in extra}}
    raw_plus_additional = pairs(core, mixed_profiles, sorted(mixed_profiles))
    def witnesses(tally, members):
        four = [key for key, (states, _) in tally.items() if states == 4]
        witnesses = []
        for site_a,site_b in sorted(four):
            i,j = core.index(site_a),core.index(site_b)
            examples = {}
            for label, genotype in sorted(members.items()):
                examples.setdefault(genotype[i]+genotype[j],label)
            witnesses.append({'markers':[site_a,site_b],'witnesses':examples})
        return witnesses
    def patterns(rows):
        return dict(sorted(Counter(n for n,_ in rows.values()).items()))
    def transitions_between(before,after):
        return dict(sorted(Counter(f'{before[k][0]} to {after[k][0]}' for k in before if before[k][0] != after[k][0]).items()))
    changed_binary = {r['marker'] for r in data['s4_vs_templates'] if het(r['s4_genotype']) != het(r['s3_and_s5_genotype'])}
    changed_allele = {r['marker'] for r in data['s4_vs_templates']}
    common = {}
    for label, exclusions in [('exclude_binary_discrepancies', changed_binary), ('exclude_allele_discrepancies', changed_allele)]:
        keys = [k for k in selection if not exclusions.intersection(k)]
        assert all(selection[k] == raw_selection[k] and combined[k] == raw_plus_additional[k] for k in keys)
        earlier = {k:selection[k] for k in keys}
        later = {k:combined[k] for k in keys}
        common[label] = {'excluded':sorted(exclusions),'marker_count':len(core)-len(exclusions),
                         'pairs':len(keys),'numbers_of_states_before':patterns(earlier),'numbers_of_states_after':patterns(later),
                         'changes':transitions_between(earlier,later)}
    new_witnesses = Counter()
    new_checks = {g:pairs(core,profiles,sorted(set(first)|{g})) for g in sorted(extra.keys()-first.keys())}
    for k in selection:
        if combined[k][0] != selection[k][0]:
            newly_informative = [g for g, tbl in new_checks.items() if tbl[k][0] != selection[k][0]]
            new_witnesses[' and '.join(newly_informative)] += 1
    # A worked example uses the counts of vines, including all replicates of a genotype.
    example = ('B_chr02_19352340', 'B_chr08_07685896')
    i, j = (core.index(site) for site in example)
    def example_counts(counts):
        counts_by_state = Counter()
        for gt, count in counts.items():
            row = profiles[gt]
            counts_by_state[row[i] + row[j]] += count
        return {state:counts_by_state[state] for state in ('00', '01', '10', '11')}
    transitions = {}
    for k in selection:
        if unknown.intersection(k):
            continue
        x,y = selection[k][1],combined[k][1]
        if x != y:
            transitions.setdefault(x+' to '+y, []).append(k)
    return {'source_doi':'10.1093/hr/uhaf237','selection_vines':sum(first.values()),'additional_vines':sum(extra.values()),
            'genotypes_in_additional_vines':len(extra),'expanded_vines_by_new_genotype':{k:extra[k] for k in sorted(extra.keys()-first.keys())},
            'paired_genotype_agreements':data['paired_genotype_agreements'],
            'two_state_to_three_state_witnesses_by_new_genotype':dict(sorted(new_witnesses.items())),
            'panel_state_counts':{'selection_template':patterns(selection),'selection_s4':patterns(raw_selection),'all_template':patterns(combined),'hybrid_s4_plus_135_templates':patterns(raw_plus_additional)},
            'selection_to_all_changes':{'template':transitions_between(selection,combined),'hybrid':transitions_between(raw_selection,raw_plus_additional)},
            'marker_subset_sensitivity':common,
            's4_vs_genotype_template_allele_disagreements':len(data['s4_vs_templates']),
            's4_vs_genotype_template_binary_disagreements':sum(het(r['s4_genotype']) != het(r['s3_and_s5_genotype']) for r in data['s4_vs_templates']),
            'panel_56_by_selection_50_specimen_sheet':summarize(raw_selection),
            'panel_56_by_s4_selection_and_s5_additional':summarize(raw_plus_additional),
            'four_state_pairs_s4_selection':witnesses(raw_selection, data['s4_profiles']),
            'four_state_pairs_s4_selection_and_s5_additional':witnesses(raw_plus_additional, mixed_profiles),
            'panel_markers_with_unresolved_ancestor':sorted(set(core)&unknown),
            'worked_pair':{'sites':example,'selection_vines':example_counts(first),'additional_vines':example_counts(extra)},
            'original_158_by_selection_50':summarize(wide),'panel_56_by_selection_50':summarize(selection),
            'panel_56_by_additional_135':summarize(additional),'panel_56_by_all_185':summarize(combined),
            'rooted_pair_changes_selection_to_combined':transitions}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--extract',type=Path,metavar='WORKBOOK')
    opt = p.parse_args()
    result = extract(opt.extract) if opt.extract else report(json.loads((HERE/'grape_inputs.json').read_text()))
    print(json.dumps(result,indent=2))
