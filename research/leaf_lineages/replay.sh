#!/usr/bin/env bash
# Run all primary results from the reduced source tables distributed in the archive.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python3 -B carrier/carrier_sets.py | diff - carrier/carrier_result.json
python3 -B carrier/leaf_omissions.py carrier/carriers.tsv | diff - carrier/omission_results.json
python3 -B completion/orientation_certificate.py carrier/carriers.tsv | diff - completion/orientation_result.json
python3 -B completion/test_orientation_certificate.py
python3 -B completion/verify_by_union.py
python3 -B topology/physical_groups.py carrier/carriers.tsv carrier/sample_roster.tsv | diff - topology/physical_groups.json
python3 -B topology/figure_isomorphism.py carrier/carriers.tsv carrier/sample_roster.tsv | diff - topology/figure_match.json
python3 -B aliquots/aliquot_controls.py | diff - aliquots/aliquot_result.json
python3 -B tropical/quartet.py | diff - tropical/quartet_result.json
python3 -B tropical/verify_quartets.py
echo 'All archived results reproduced.'
