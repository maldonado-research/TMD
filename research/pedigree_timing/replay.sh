#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
check() {
    expected=$1
    shift
    python3 -B "$@" > "$tmpdir/actual"
    cmp "$tmpdir/actual" "$expected"
}
check kennedy/results.json kennedy/score_timing.py
check divisions/results.json divisions/resolution.py
check mouse/mouse_results.json mouse/score_mouse.py
check fruit/results.json fruit/replay.py
check shorea/satake_placements.json shorea/satake_branches.py
check shorea/satake_patterns.json shorea/satake_branches.py --extract shorea/elife-88456-supp1-v1.xlsx
python3 -B shorea/verify_satake.py --workbook shorea/elife-88456-supp1-v1.xlsx
check shorea/panel_budget/aggregate.json shorea/panel_budget/verify_satake_workbook.py shorea/elife-88456-supp1-v1.xlsx
echo "Verified the yeast, tree, fruit and mouse results."
