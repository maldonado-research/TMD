#!/usr/bin/env python3
"""MIT: read-only integrity/admission checks; no requests or biological validation."""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(path, record):
    raw = path.read_bytes()
    require(len(raw) == record["bytes"], f"Byte mismatch: {path.name}")
    require(hashlib.sha256(raw).hexdigest() == record["sha256"],
            f"SHA256 mismatch: {path.name}")


def response_markdown(capture):
    response = capture["response"]
    structured = response.get("structuredContent", {})
    if isinstance(structured, dict) and isinstance(structured.get("markdown"), str):
        return structured["markdown"]
    for block in response.get("content", []):
        if block.get("type") == "text":
            try:
                value = json.loads(block["text"])
            except (ValueError, TypeError):
                continue
            if isinstance(value, dict) and isinstance(value.get("markdown"), str):
                return value["markdown"]
    raise ValueError("No authenticated markdown representation in capture")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    parser.add_argument("--shared-source-cache", type=Path)
    args = parser.parse_args()
    require(sys.flags.optimize == 0, "Run ordinary Python without -O or -OO")
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    public = read(package / "PUBLIC_FILES.json")
    expected_names = set(public["public_files"])
    require(len(public["public_files"]) == len(expected_names), "Duplicate public filenames")
    require({p.name for p in package.iterdir()} == expected_names, "Public allowlist mismatch")
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()),
            "Only regular public files are admitted")
    records = {record["path"]: record for record in public["files"]}
    require(len(records) == len(public["files"]), "Duplicate public hash records")
    unhashed = {"PUBLIC_FILES.json", "SHA256SUMS.txt", "VERIFICATION_RECEIPT.json"}
    require(set(records) == expected_names - unhashed, "Incomplete public core hash coverage")
    for name, record in records.items():
        require(Path(name).name == name, "Public path must be a basename")
        identity(package / name, record)
    sums = {}
    for line in (package / "SHA256SUMS.txt").read_text().splitlines():
        expected, name = line.split("  ", 1)
        require(name not in sums and Path(name).name == name, "Invalid SHA256SUMS entry")
        require(name in expected_names, "Unlisted SHA256SUMS file")
        require(hashlib.sha256((package / name).read_bytes()).hexdigest() == expected,
                f"SHA256SUMS mismatch: {name}")
        sums[name] = expected
    require(set(sums) == expected_names - {"SHA256SUMS.txt", "VERIFICATION_RECEIPT.json"},
            "Incomplete SHA256SUMS coverage")
    contract = read(package / "CONTROL_CONTRACT.json")
    decision = read(package / "DECISION.json")
    provenance = read(package / "SOURCE_PROVENANCE.json")
    study = read(root / "research/prospective_design/REGISTRY_CANDIDATE.json")
    native = read(root / "research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json")
    study_fields = study["study_inputs_requiring_resolution"]
    native_fields = native["actual_values"]
    require(len(study_fields) == 26 and all(v is None for v in study_fields.values()),
            "Actual study registry is not 26 NULL fields")
    require(len(native_fields) == 18 and all(v is None for v in native_fields.values()),
            "Native planning registry is not 18 NULL fields")
    require(contract["mandatory_categories"] == study["mandatory_outcome_ledger_categories"],
            "Endpoint ledger category drift")
    require(contract["preserved_model"]["axis_s"] == study["frozen_algorithm_candidate"]["axis_s"],
            "Axis drift")
    require(contract["preserved_model"]["route_order"] == study["frozen_algorithm_candidate"]["route_order"],
            "Route-order drift")
    require(len(contract["components"]) == 8, "Missing control component")
    require(len({c["id"] for c in contract["components"]}) == 8, "Duplicate control IDs")
    for component in contract["components"]:
        require(component["actual_protocol_selected"] is False, "Unexpected protocol selection")
        require(component["admission"] == "NOT_ADMITTED_REQUIRE_QUALIFIED_ASSESSMENT",
                "Unexpected biological admission")
        for field in ("unit", "denominator", "required_fields", "available_evidence", "not_supplied", "failure_rule"):
            require(bool(component[field]), f"Missing contract field {field}")
    for document in (contract, decision):
        require(document["preserved_blockers"] == ["R5", "R11", "R17"], "Blocker drift")
        require(document["actual_study_inputs_resolved"] == 0, "Study field promoted")
        require(document["native_planning_inputs_resolved"] == 0, "Planning field promoted")
        require(document["admitted_matched_panels"] == 0, "Panel admitted unexpectedly")
    for flag in ("forecasts_eta_count_law_error_stopping_changed", "paused_runner_changed",
                 "methods_0_6_0_changed", "new_experiment", "biological_confirmation",
                 "qualified_external_review", "laboratory_protocol_or_partner_selected"):
        require(decision[flag] is False, f"Unexpected decision change: {flag}")
    for record in provenance["project_records_read"]:
        identity(root / record["path"], record)
    acquisitions = provenance["branch_scientific_acquisitions"]
    require(len(acquisitions) == 1, "Unexpected branch acquisition count")
    totals = provenance["branch_totals"]
    require(totals["logical_source_calls"] == 1 and totals["failures"] == 0,
            "Branch source count drift")
    require(totals["counted_acquisition_bytes"] == sum(a["bytes"] for a in acquisitions),
            "Branch byte accounting mismatch")
    own_replay = "UNRUN: source cache not supplied"
    if args.source_cache is not None:
        for record in acquisitions:
            path = args.source_cache / record["capture_filename"]
            identity(path, record)
            captured = read(path)
            for key in ("tool", "args", "started_at_utc", "captured_at_utc"):
                require(captured[key] == record[key], f"Capture provenance mismatch: {key}")
            require(captured["response"].get("isError") is False, "Watch call failed")
            require(captured["response"]["structuredContent"]["results"] == [],
                    "Watch result is not empty")
        own_replay = "PASS: one exact empty watch response"
    shared_replay = "UNRUN: shared source cache not supplied"
    if args.shared_source_cache is not None:
        for record in provenance["shared_acquisitions_reused_without_new_requests"]:
            path = args.shared_source_cache / record["capture_filename"]
            identity(path, record)
            captured = read(path)
            for key in ("tool", "args", "started_at_utc", "captured_at_utc"):
                require(captured[key] == record[key], f"Shared capture provenance mismatch: {key}")
        supplement = response_markdown(read(args.shared_source_cache / "04_supplement_pdf.json"))
        for anchor in ("lysogeny broth (LB) was used instead of KB", "*pvdS* was deleted",
                       "pCdrA-mScarlet", "3 or 4 inoculum densities were tested for each strain"):
            require(anchor in supplement, f"Supplement anchor absent: {anchor}")
        shared_replay = "PASS: three existing source representations and four text anchors; no exact PDF authentication"
    print(json.dumps({
        "status": "PASS", "checks": "Artifact identity, source anchors where supplied, declared contract and unchanged null/admission invariants",
        "study_fields_NULL": len(study_fields), "native_fields_NULL": len(native_fields),
        "project_artifacts_verified": len(provenance["project_records_read"]),
        "control_components": len(contract["components"]), "own_source_replay": own_replay,
        "shared_source_replay": shared_replay,
        "public_allowlist_and_core_hashes": "PASS; receipt excluded to avoid verification cycles",
        "not_validated": ["experimental truth", "control independence or transport", "count law", "biological mechanism", "qualified external review"]
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}))
        sys.exit(1)
