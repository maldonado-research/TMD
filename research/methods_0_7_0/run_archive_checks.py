#!/usr/bin/env python3
"""Verify archive integrity and replay bounded checks in an isolated copy.

Copyright (c) 2026 Ricardo Maldonado. MIT; see LICENSE.
No network access or external source acquisition is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest():
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    listed = {row["path"]: row for row in manifest["files"]}
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()}
    assert actual == set(listed) | {"MANIFEST.json"}, "Archive file inventory differs"
    for name, row in listed.items():
        path = ROOT / name
        assert not path.is_symlink(), name
        assert path.stat().st_size == row["bytes"], name
        assert sha256(path) == row["sha256"], name
    return len(listed)


def check_inherited_hashes():
    manifests = [
        "conditional_curvature/independent_oracle_hashes.json",
        "conditional_design/ORACLE_HASHES.json",
        "conditional_recovery/INDEPENDENT_HASHES.json",
        "classification_bounds/INDEPENDENT_HASHES.json",
        "eligibility_gate_bounds/INDEPENDENT_HASHES.json",
        "threshold_calibration/INDEPENDENT_HASHES.json",
    ]
    integrated_hashes = ROOT / "research/integrated_inference/INDEPENDENT_HASHES.json"
    if integrated_hashes.exists():
        manifests.append("integrated_inference/INDEPENDENT_HASHES.json")
    checks = 0
    for relative in manifests:
        path = ROOT / "research" / relative
        doc = json.loads(path.read_text())
        hashes = doc.get("files", doc.get("sha256", doc))
        for name, expected in hashes.items():
            target = (path.parent / name).resolve()
            assert target.is_relative_to(ROOT), name
            assert sha256(target) == expected, (str(path), name)
            checks += 1
    inventory = ROOT / "research/eligibility_gate_bounds/source_audit/PUBLIC_FILES.json"
    for name in json.loads(inventory.read_text())["files"]:
        assert (inventory.parent / name).is_file(), name
    for line in (inventory.parent / "SHA256SUMS.txt").read_text().splitlines():
        expected, name = line.split(None, 1)
        assert sha256(inventory.parent / name.strip()) == expected, name
        checks += 1
    return checks


def check_source_provenance():
    provenance = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())
    for row in provenance["original_source_files"]:
        path = ROOT / row["path"]
        assert path.stat().st_size == row["bytes"], row["path"]
        assert sha256(path) == row["sha256"], row["path"]
    registry = ROOT / "research/prospective_design/REGISTRY_CANDIDATE.json"
    assert sha256(registry) == "80d96b15a8fd6ed61c4ba440d423972d5ce73e8563403b38d5fae8b608b7b54c"
    assert json.loads(registry.read_text())["document_status"] == "design_candidate_not_registered"
    return len(provenance["original_source_files"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-only", action="store_true")
    parser.add_argument("--scratch-directory", type=Path)
    parser.add_argument("--output", type=Path, help="Write a fresh receipt outside the archive")
    args = parser.parse_args()
    if args.output and args.output.resolve().is_relative_to(ROOT):
        raise ValueError("Receipt must be outside the immutable archive tree")
    result = {
        "status": "pass",
        "manifest_files_checked": check_manifest(),
        "inherited_hash_entries_checked": check_inherited_hashes(),
        "original_source_files_checked": check_source_provenance(),
        "python": sys.version.split()[0],
        "network_used": False,
        "native_validation": False,
        "external_peer_review": False,
        "source_authentication_replayed": False,
        "scope": "Bounded computational archive replay; preserved larger oracle receipts are hash verified, not all recomputed.",
        "checks": [],
    }
    if not args.manifest_only:
        if args.scratch_directory:
            args.scratch_directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="tmd-methods-replay-", dir=args.scratch_directory) as folder:
            work = Path(folder) / "package"
            shutil.copytree(ROOT, work)
            jobs = [
                ("conditional_curvature", ["research/conditional_curvature/verify_conditional.py"], "research/conditional_curvature/VERIFICATION.json"),
                ("conditional_design", ["research/conditional_design/verify_design_diagnostics.py", "--repo", ".", "--output", "research/conditional_design/VERIFICATION.json"], "research/conditional_design/VERIFICATION.json"),
                ("conditional_recovery", ["research/conditional_recovery/verify_recovery.py"], "research/conditional_recovery/VERIFICATION.json"),
                ("classification_bounds", ["research/classification_bounds/verify_bounds.py"], "research/classification_bounds/VERIFICATION.json"),
                ("eligibility_gate_bounds", ["research/eligibility_gate_bounds/verify_eligibility_gate.py", "--repository", "."], "research/eligibility_gate_bounds/VERIFICATION.json"),
                ("threshold_calibration", ["research/threshold_calibration/verify_threshold_calibration.py", "--repository", "."], "research/threshold_calibration/VERIFICATION.json"),
                ("classification_independent_comparison", ["research/classification_bounds/compare_frozen_producer.py"], "research/classification_bounds/PRODUCER_COMPARISON_RECEIPT.json"),
                ("threshold_independent_comparison", ["research/threshold_calibration/compare_frozen_threshold.py", "--producer-dir", "research/threshold_calibration", "--repository", ".", "--output", "research/threshold_calibration/PRODUCER_COMPARISON_RECEIPT.json"], "research/threshold_calibration/PRODUCER_COMPARISON_RECEIPT.json"),
            ]
            integrated = work / "research/integrated_inference/verify_integrated_inference.py"
            if integrated.exists():
                jobs.append(("integrated_inference", [str(integrated.relative_to(work)), "--repository", "."], "research/integrated_inference/VERIFICATION.json"))
                jobs.append(("integrated_independent_comparison", ["research/integrated_inference/compare_frozen_integration.py", "--producer-dir", "research/integrated_inference", "--repository", ".", "--output", "research/integrated_inference/PRODUCER_COMPARISON_RECEIPT.json"], "research/integrated_inference/PRODUCER_COMPARISON_RECEIPT.json"))
                jobs.append(("integrated_independent_exact_oracle", ["research/integrated_inference/independent_integrated_oracle.py", "--output", "research/integrated_inference/INDEPENDENT_EXACT_RECEIPT.json"], "research/integrated_inference/INDEPENDENT_EXACT_RECEIPT.json"))
            for label, command, receipt in jobs:
                completed = subprocess.run([sys.executable, "-B", *command], cwd=work, capture_output=True, text=True, timeout=240)
                if completed.returncode:
                    raise RuntimeError(f"{label}: {completed.stderr[-4000:]} {completed.stdout[-1000:]}")
                emitted = json.loads((work / receipt).read_text())
                expected = json.loads((ROOT / receipt).read_text())
                assert emitted == expected, f"Saved receipt mismatch: {label}"
                result["checks"].append({"name": label, "status": "pass", "saved_receipt_matches": True, "receipt_sha256": sha256(ROOT / receipt)})
                print(f"PASS {label}", file=sys.stderr, flush=True)
            fixtures = sorted(work.glob("research/*/example*.json"))
            for fixture in fixtures:
                original = ROOT / fixture.relative_to(work)
                assert fixture.read_bytes() == original.read_bytes(), f"Regenerated fixture mismatch: {fixture.name}"
            result["saved_fixture_files_checked"] = len(fixtures)
            cli_checks = []
            for plan in sorted((work / "research/integrated_inference").glob("example_*_plan.json")):
                prefix = plan.name.removesuffix("_plan.json")
                observations = plan.with_name(prefix + "_observations.json")
                expected_path = plan.with_name(prefix + "_result.json")
                command = [sys.executable, "-B", "research/integrated_inference/integrated_inference.py", "--plan", str(plan.relative_to(work)), str(observations.relative_to(work)), "--repository", "."]
                completed = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=120, check=True)
                output = json.loads(completed.stdout)
                assert output.pop("plan_file_sha256") == sha256(plan)
                assert output.pop("observation_file_sha256") == sha256(observations)
                assert output == json.loads(expected_path.read_text()), prefix
                cli_checks.append(prefix)
            result["integrated_cli_fixture_replays"] = cli_checks
            command = [sys.executable, "-B", "research/conditional_recovery/verify_measurement_bridge.py"]
            completed = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=60, check=True)
            bridge = json.loads(completed.stdout)
            assert bridge["status"] == "PASS_COUNTEREXAMPLE_SOURCE_UNRUN"
            result["measurement_bridge"] = {"status": bridge["status"], "check_count": bridge["check_count"]}
    assert check_manifest() == result["manifest_files_checked"]
    result["archive_unchanged_after_replay"] = True
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
