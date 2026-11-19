#!/usr/bin/env bash
# Replay the published calculations from their packaged inputs.
set -euo pipefail

sources=()
if (( $# )); then
    if [[ $1 != --sources || $# != 9 ]]; then
        echo 'Usage: bash replay.sh [--sources Wang-S1.xlsx Wang-S2.xlsx Ji-S7.xlsx Ji-S11.xlsx Wang-GZ.docx Johnson-S1.xlsx Johnson-S2.zip Pine-Figure7.pdf]' >&2
        exit 2
    fi
    shift
    for source in "$@"; do
        if [[ $source != /* ]]; then source="$PWD/$source"; fi
        sources+=("$source")
    done
fi

cd -- "$(dirname -- "$0")"
python3 -B peach/peach_reads.py | diff - peach/peach_result.json
python3 -B peach/read_limits.py | diff - peach/read_limits.json
python3 -B peach/verify_peach_gate.py ../leaf_lineages/carrier/carriers.tsv peach/peach_inputs.json | diff - peach/peach_gate.json
python3 -B yeast/yeast_events.py | diff - yeast/yeast_result.json
python3 -B yeast/horizons.py | diff - yeast/horizons.json
python3 -B pine/figure7_counts.py | diff - pine/figure7_results.json

# Match the two independently decoded contingency tables before using the counts.
python3 -B - <<'PY'
import csv
import json
from pathlib import Path

vector = json.loads(Path('pine/fig7_counts.json').read_text())
with Path('pine/figure7_counts.tsv').open() as stream:
    cells = [dict(group=row['family_panel'], genotype=row['genotype'],
                  dwarf=int(row['dwarf']), normal=int(row['normal']))
             for row in csv.DictReader(stream, delimiter='\t')]
assert vector['cells'] == cells
assert vector['dots'] == sum(c['dwarf'] + c['normal'] for c in cells)
PY

# Recompute the independent verifier's endpoint and sampling-grid summaries
# from the reduced observations. The optional native check also reads the
# publication's read counts, roster, and two file digests.
python3 -B - <<'PY'
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, "yeast")
from verify_visits import summarize

expected = json.loads(Path("yeast/verify_result.json").read_text())
groups = defaultdict(lambda: defaultdict(list))
types = defaultdict(dict)
row_counts = Counter()
disagreements = defaultdict(Counter)
with Path("yeast/yeast_observations.tsv").open() as stream:
    for row in csv.DictReader(stream, delimiter="\t"):
        well, group = row["well"], row["group"]
        states = [-1 if s == "?" else int(s) for s in row["visits"]]
        groups[well][group].append(states)
        assert types[well].setdefault(group, row["class"]) == row["class"]
        row_counts[well] += 1
        for state, flag in zip(states, row["archived_present"]):
            disagreements[well]["compared"] += 1
            if flag == "1" and state < 1:
                disagreements[well]["flagged_but_not_local"] += 1
            if flag == "0" and state >= 1:
                disagreements[well]["local_but_not_flagged"] += 1
for key, include_all in (("all_initially_haploid", True), ("excluding_autodiploidized_P1B03", False)):
    wells = {w: g for w, g in groups.items() if include_all or w != "P1B03"}
    observed = summarize(wells, types, row_counts, disagreements, details=include_all)
    assert json.loads(json.dumps(observed)) == expected[key], key
print("Independent yeast event and sampling-grid summaries agree for both cohorts.")
PY

if (( ${#sources[@]} )); then
    python3 -B peach/peach_reads.py --extract "${sources[@]:0:5}" | diff - peach/peach_inputs.json
    python3 -B peach/s11_crosswalk.py "${sources[3]}" ../leaf_lineages | diff - peach/s11_crosswalk.json
    python3 -B peach/s7_native_audit.py "${sources[2]}" "${sources[3]}" ../leaf_lineages | diff - peach/s7_native_result.json
    python3 -B yeast/yeast_events.py --extract "${sources[5]}" "${sources[6]}" | diff - yeast/yeast_observations.tsv
    python3 -B yeast/verify_visits.py "${sources[5]}" "${sources[6]}" | diff - yeast/verify_result.json
    python3 -B pine/figure7_counts.py --extract "${sources[7]}" | diff - pine/figure7_counts.tsv
    python3 -B pine/extract_points.py "${sources[7]}" | diff - pine/fig7_counts.json
    echo 'Native workbook, document, ZIP and figure extractions agree.'
fi
echo 'All packaged transmission and timing calculations reproduced.'
