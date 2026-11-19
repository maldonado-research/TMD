#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
out=$(mktemp -d)
trap 'rm -rf -- "$out"' EXIT
python3 -B fasanello/score_pairs.py | diff - fasanello/pair_results.json
python3 -B fasanello/technical.py fasanello/technical_counts.tsv | diff - fasanello/technical_results.json
python3 -B fasanello/pool_choices.py | diff - fasanello/pool_results.json
python3 -B fasanello/verify_envelope.py fasanello/technical_counts.tsv --out-dir "$out"
for file in endpoint_envelope.json endpoint_envelope_wells.tsv; do
    cmp "$out/$file" "fasanello/$file"
done
echo 'All bundled two-label scores and repeat-measurement comparisons reproduced.'
