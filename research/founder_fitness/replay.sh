#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
python3 -B score.py > "$tmpdir/scores.json"
cmp "$tmpdir/scores.json" results.json
python3 -B library_sensitivity/check_libraries.py > "$tmpdir/libraries.json"
cmp "$tmpdir/libraries.json" library_sensitivity/library_results.json
python3 -B proof_assay/verify_proof.py > "$tmpdir/proof.json"
cmp "$tmpdir/proof.json" proof_assay/proof_results.json
python3 -B proof_assay/check_proof_endpoints.py > "$tmpdir/proof_endpoints.json"
cmp "$tmpdir/proof_endpoints.json" proof_assay/proof_endpoint_results.json
echo "Verified main, pooled-endpoint and separate founder-assay forecasts."
