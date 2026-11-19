#!/usr/bin/env bash
# Compare all stored results with a new run on the archived inputs.
set -euo pipefail
cd -- "$(dirname -- "$0")"
carriers=../leaf_lineages/carrier/carriers.tsv
roster=../leaf_lineages/carrier/sample_roster.tsv
python3 -B edits/mixed_frontier.py "$carriers" | diff - edits/mixed_result.json
python3 -B edits/mixed_frontier.py --require-all-markers "$carriers" | diff - edits/mixed_result.json
python3 -B edits/witnesses.py "$carriers" | diff - edits/witness_result.json
python3 -B edits/test_mixed_frontier.py
python3 -B edits/independent/mutation_trees.py "$carriers" | diff - edits/independent/results.json
python3 -B edits/independent/weight_frontier.py "$carriers" | diff - edits/independent/weighted_result.json
python3 -B edits/independent/test_mutation_trees.py
python3 -B mixtures/row_split_witness.py "$carriers" "$roster" | diff - mixtures/row_split_witness.json
python3 -B mixtures/figure_oracle.py | diff - mixtures/figure_result.json
python3 -B mixtures/one_missing_call.py | diff - mixtures/one_missing_result.json
python3 -B grape/grape_panels.py | diff - grape/grape_result.json
python3 -B sources/leaf_run_crosswalk.py --historical ../leaf_lineages | diff - sources/leaf_run_result.json
echo 'All lineage-model calculations reproduced.'
