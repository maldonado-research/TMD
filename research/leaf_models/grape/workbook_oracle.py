"""Audit unordered genotype calls and pair patterns directly in the Tempranillo XLSX XML."""
import argparse
import csv
import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SHA256 = "135002ebe85ea2307238cf7d866e7b799fdf27968e1f628a67ed76c91fae1b60"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def sheets(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SHA256
    with ZipFile(path) as archive:
        shared = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = ["".join(t.text or "" for t in item.iter(NS+"t")) for item in shared]
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        assert [s.attrib["name"] for s in book.iter(NS+"sheet")] == [f"Sup_file_{i}" for i in range(1,6)]
        tables = []
        for i in range(1,6):
            root = ET.fromstring(archive.read(f"xl/worksheets/sheet{i}.xml"))
            records = []
            for row in root.iter(NS+"row"):
                record = {}
                for cell in row.iter(NS+"c"):
                    raw = cell.findtext(NS+"v")
                    if raw is not None:
                        col = re.fullmatch(r"([A-Z]+)\d+",cell.attrib["r"])[1]
                        index = 0
                        for c in col:
                            index = index*26+ord(c)-64
                        record[index-1] = strings[int(raw)] if cell.get("t")=="s" else raw
                if record:
                    records.append(record)
            tables.append(records[1:])
    return tables


def normalize(call):
    a,b = call.split(":")
    assert a in "ACGT" and b in "ACGT"
    return ":".join(sorted((a,b)))


def hetero(call):
    return call[0] != call[-1]


def summarize(source, complete, loci, keep, representation):
    """Locus-specific state labels are invariant to how the two states are oriented."""
    original_spectrum, combined_spectrum = Counter(),Counter()
    changed = Counter()
    examples = []
    for j,k in itertools.combinations(keep,2):
        def state(r):
            return (representation(r[j]), representation(r[k]))
        old = {state(row) for row in source.values()}
        new = {state(row) for row in complete.values()}
        assert old <= new
        original_spectrum[len(old)] += 1
        combined_spectrum[len(new)] += 1
        if old != new:
            changed[f"{len(old)}_to_{len(new)}"] += 1
            if loci[j]=="B_chr02_19352340" and loci[k]=="B_chr08_07685896":
                for pair in sorted(new):
                    example = min(n for n,row in complete.items() if state(row)==pair)
                    examples.append({'state':pair,'sample':example,'new':pair not in old})
    return {'markers':len(keep),'original_50':dict(sorted(original_spectrum.items())),
            'combined_185':dict(sorted(combined_spectrum.items())),'changed_pairs':dict(sorted(changed.items())),
            'worked_pair_B_chr02_19352340_and_B_chr08_07685896':examples}


def verify(path):
    s1,s2,s3,s4,s5 = sheets(path)
    roster = {r[0]:(r[8],r[12]) for r in s1[1:] if r[0].startswith("Tempranillo-")}
    assert len(roster)==185
    loci = [s5[0][i] for i in range(2,58)]
    selected = {r[0] for r in s2[1:] if r[6]=="Yes"}
    assert set(loci) == selected
    profiles = {r[0]:tuple(normalize(r[i]) for i in range(2,58)) for r in s5[1:]}
    counts = Counter(gt for source,gt in roster.values())
    assert counts == {r[0]:int(r[1]) for r in s5[1:]}
    s3index = {g:i for i,g in s3[0].items() if i>=2}
    inferred = next(r for r in s3[1:] if r[0]=="Ancestral TT")
    missing = [g for g,i in s3index.items() if inferred[i]=="-"]
    old_classes = {r[0]:r for r in s3[1:] if r[0].startswith('GT-')}
    assert all(profiles[g] == tuple(normalize(r[s3index[loc]]) for loc in loci) for g,r in old_classes.items())
    assert all(normalize(r[i]) for r in old_classes.values() for i in s3index.values())
    full = {sample:profiles[g] for sample,(use,g) in roster.items()}
    new = {n:r for n,r in full.items() if roster[n][0]=="TG"}
    previous = {n:r for n,r in full.items() if n not in new}
    sample_calls = {}
    paired_calls = 0
    discrepancies = []
    lookup = {}
    for i,label in s4[0].items():
        if i>=2:
            platform,site = label.split(" - ",1)
            lookup[site.strip(),platform] = i
    for r in s4[1:]:
        sample,gt = r[0],r[1]
        assert roster[sample][1]==gt and gt in old_classes
        measured = []
        for i,g in enumerate(loci):
            one = normalize(r[lookup[g,"Illumina"]])
            two = normalize(r[lookup[g,"Fluidigm"]])
            assert one==two
            paired_calls += 1
            measured.append(one)
            assigned = profiles[gt][i]
            if assigned != one:
                discrepancies.append({'sample':sample,'GT':gt,'site':g,'S4':one,'S3_and_S5':assigned,
                                      'changes_heterozygosity':hetero(one)!=hetero(assigned)})
        sample_calls[sample] = tuple(measured)
    assert previous.keys()==sample_calls.keys() and len(new)==135
    hybrid = sample_calls | new
    suspect = {d['site'] for d in discrepancies}
    suspect_binary = {d['site'] for d in discrepancies if d['changes_heterozygosity']}
    scopes = {'all_56':range(len(loci)),'exclude_all_discrepant': [i for i,g in enumerate(loci) if g not in suspect],
              'exclude_only_heterozygosity_discrepant':[i for i,g in enumerate(loci) if g not in suspect_binary]}
    report={}
    for key,ids in scopes.items():
        a = summarize(previous,full,loci,ids,hetero)
        b = summarize(sample_calls,hybrid,loci,ids,hetero)
        report[key] = {'S5_genotype_profiles':a,'S4_observed_plus_S5_for_additional_vines':b}
        if key!='all_56':assert a == b
    i9,i10 = map(loci.index,['B_chr09_06530273','B_chr10_05943585'])
    categorical = {}
    for sample,row in sorted(hybrid.items()):
        pair = row[i9]+' / '+row[i10]
        if pair not in categorical:
            categorical[pair] = {'example_sample':sample,'GT':roster[sample][1],'S4':sample in sample_calls,'vines':0}
        categorical[pair]['vines']+=1
    new_classes = set(profiles)-set(old_classes)
    new_witness = Counter()
    singletons = {g:[] for g in new_classes}
    for j,k in itertools.combinations(scopes['exclude_all_discrepant'],2):
        old = {(hetero(r[j]),hetero(r[k])) for r in previous.values()}
        for g in sorted(new_classes):
            r=profiles[g]
            if (hetero(r[j]),hetero(r[k])) not in old:
                new_witness[g]+=1
                singletons[g].append([loci[j],loci[k]])
    return {'xlsx_sha256':SHA256,'S1_purpose_counts':dict(sorted(Counter(use for use,gt in roster.values()).items())),
            'S4_matching_interplatform_site_vine_measurements':paired_calls,
            'additional_135_distinct_GT_labels':len({roster[n][1] for n in new}),
            'additional_135_variable_binary_markers':sum(len({hetero(row[i]) for row in new.values()})>1 for i in range(56)),
            'S3_missing_ancestral_states':missing,'S3_missing_ancestral_states_in_selected_56':sorted(set(loci)&set(missing)),
            'S4_against_S3_and_S5':discrepancies,'binary_pair_spectra':report,
            'new_class_clean_pairs':dict(sorted(singletons.items())),
            'nominal_unordered_hybrid_56':summarize(sample_calls,hybrid,loci,scopes['all_56'],str),
            'B_chr09_06530273_B_chr10_05943585_unordered_hybrid_witness':categorical}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('workbook',type=Path)
    print(json.dumps(verify(p.parse_args().workbook),indent=2))
