#!/bin/sh
set -eu
cd "$(dirname "$0")"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
for folder in mouse matched oak; do
    case "$folder" in
        mouse) entry=score_mouse.py ;;
        matched) entry=marker_pairing.py ;;
        oak) entry=audit_oak.py ;;
    esac
    (cd "$folder" && python3 -B "$entry") > "$tmpdir/$folder.json"
    diff "$folder/results.json" "$tmpdir/$folder.json"
done
(cd litters && python3 -B split_test.py) > "$tmpdir/litters.json"
diff litters/split_results.json "$tmpdir/litters.json"
(cd litters && python3 -B verify_split.py)
(cd oak && python3 -B audit_oak.py --branch-tsv) > "$tmpdir/oak.tsv"
diff oak/branch_contrasts.tsv "$tmpdir/oak.tsv"
printf '%s\n' 'Verified mouse forecasts, matched-marker comparisons, litter allocations and oak bounds.'
