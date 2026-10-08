"""R19 synthetic ledger integrity and optional cached-source anchor checks.

Passing validates this bookkeeping example, not biological admission, mutation
rates, ascertainment probabilities, independent trials, or a clinical result.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
STAGES = ("available_at_collection", "isolated", "outgrown", "sequenced")
STOPS = ("division", "collection", "death", "lost_tracking")
CALLS = ("toy_validated_alternate", "toy_validated_reference", "unknown")
MAX_RECORDS = 10000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def runtime_guard():
    if not __debug__:
        raise RuntimeError("Verification requires ordinary Python without -O/-OO")


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON field")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("Nonfinite JSON value")
    content = Path(path).read_bytes()
    require(len(content) <= 2_000_000, "Input JSON size cap exceeded")
    return json.loads(content, object_pairs_hook=unique, parse_constant=constant)


def rational(value):
    require(type(value) in (int, str) and type(value) is not bool,
            "Times require exact rational integers or strings")
    if type(value) is str:
        require(len(value) <= 24 and re.fullmatch(
            r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value) is not None,
            "Malformed rational time")
    result = Fraction(value)
    require(result >= 0 and max(result.numerator.bit_length(),
            result.denominator.bit_length()) <= 32, "Time outside supported domain")
    return result


def rows(value, key):
    require(type(value) is list and 0 < len(value) <= MAX_RECORDS,
            key + " must be a nonempty bounded table")
    require(all(type(x) is dict for x in value), key + " rows must be objects")
    result = {x[key]: x for x in value}
    require(len(result) == len(value), "Duplicate " + key)
    require(all(type(x) is str and x and len(x) <= 128 for x in result),
            "Identifiers must be short nonempty strings")
    return result


def verify_ledger(ledger, rules, rules_hash):
    runtime_guard()
    require(ledger["provenance"] == "SYNTHETIC" and
            ledger["record_id"] == "R000019" and
            type(ledger["schema_version"]) is int and ledger["schema_version"] == 1,
            "Only the synthetic R19 schema is admitted")
    require(ledger["toy_rules_sha256"] == rules_hash,
            "Toy rule bytes changed without matching the frozen ledger")
    require(ledger["toy_locks_fixed_before_toy_observations"] is True,
            "Toy lock declaration missing")
    require(rules["provenance"] == "SYNTHETIC" and
            type(rules["minimum_positive_descendants"]) is int and
            rules["minimum_positive_descendants"] == 2 and
            type(rules["minimum_negative_outgroup_descendants"]) is int and
            rules["minimum_negative_outgroup_descendants"] == 1 and
            rules["ancestor_reference_status"] == "simulated_only",
            "Unsupported or altered toy ascertainment rule")
    design = ledger["design_status"]
    for key in ("actual_system", "actual_route_catalog", "actual_axis",
                "actual_event_inclusion_predicate", "actual_error_stopping_plan",
                "actual_count_law", "actual_partner_protocol"):
        require(design[key] is None, "Actual study choice cannot be invented by this fixture")
    require(type(design["actual_registry_fields_resolved"]) is int and
            design["actual_registry_fields_resolved"] == 0 and
            design["biological_admission"] == "blocked", "Registry/admission claim rejected")
    for key in ("first_arrival_count_law_admitted", "binomial_or_poisson_count_law_admitted",
                "confidence_power_or_cancer_outcome_claim"):
        require(ledger[key] is False, "Scientific claim is outside ledger verification")
    require(ledger["stage_control_measurements"] == [] and
            ledger["event_inclusion_control_measurements"] == [],
            "This toy has no calibrated control ledger")
    cultures = rows(ledger["cultures"], "culture_id")
    cells = rows(ledger["cells"], "cell_id")
    divisions = rows(ledger["divisions"], "division_id")
    assignments = rows(ledger["origin_assignments"], "assignment_id")
    collection = rational(ledger["collection_time"])
    require(ledger["time_unit"] == "arbitrary_synthetic_time_units",
            "Synthetic exposure units must remain explicit")
    children = {cell: [] for cell in cells}
    samples = {}
    for cid, cell in cells.items():
        require(cell["culture_id"] in cultures, "Cell culture is unknown")
        birth, stop = rational(cell["birth_time"]), rational(cell["stop_time"])
        require(birth < stop <= collection, "Cell interval is invalid")
        require(cell["stop_reason"] in STOPS and
                cell["imaging_status"] == "identity_tracked_until_stop",
                "Stop/imaging status unsupported")
        parent = cell["parent_cell_id"]
        if parent is not None:
            require(parent in cells and parent != cid, "Missing or self parent")
            require(cells[parent]["culture_id"] == cell["culture_id"] and
                    cells[parent]["stop_reason"] == "division" and
                    rational(cells[parent]["stop_time"]) == birth,
                    "Parent, culture and birth time disagree")
            children[parent].append(cid)
        stage = cell["stages"]
        require(set(stage) == set(STAGES) and all(type(stage[k]) is bool for k in STAGES),
                "Stage flags must be explicit booleans")
        require(all(not stage[STAGES[i+1]] or stage[STAGES[i]] for i in range(3)),
                "Cell recovery stages are not nested")
        if cell["stop_reason"] != "collection":
            require(not any(stage.values()), "Dead/lost/dividing cell is not collection-available")
        else:
            require(stop == collection and stage["available_at_collection"],
                    "Collection-available terminal is inconsistent")
        require(cell["unknown_genotype_is_a_negative_call"] is False,
                "Unknown genotype cannot become a reference call")
        if stage["sequenced"]:
            sample = cell["sample_id"]
            require(type(sample) is str and sample and sample not in samples,
                    "Sequenced sample ID is missing or duplicated")
            samples[sample] = cid
            require(cell["genotype_status"] == "toy_assayed", "Sequenced genotype flag disagrees")
        else:
            require(cell["sample_id"] is None and cell["genotype_status"] == "unknown",
                    "Unsequenced cell lacks a direct genotype")
    for culture_id, culture in cultures.items():
        root = culture["founder_cell_id"]
        roots = [cid for cid, cell in cells.items()
                 if cell["culture_id"] == culture_id and cell["parent_cell_id"] is None]
        require(roots == [root] and culture["founder_reference_status"] == "simulated_only",
                "Founder/reference declaration disagrees with pedigree")
        require(culture["related_descendants_are_independent_biological_replicates"] is False,
                "Related descendants cannot be promoted to independent replicates")
        require(type(culture["dependence_group_id"]) is str and culture["dependence_group_id"],
                "Founder dependence group is missing")
    for cid, cell in cells.items():
        require(len(children[cid]) == (2 if cell["stop_reason"] == "division" else 0),
                "Binary division and daughter ledger disagree")
        seen = set()
        ancestor = cid
        while ancestor is not None:
            require(ancestor not in seen, "Pedigree cycle")
            seen.add(ancestor)
            ancestor = cells[ancestor]["parent_cell_id"]
    division_parents = set()
    for division in divisions.values():
        parent = division["parent_cell_id"]
        require(parent in cells and parent not in division_parents,
                "Division parent missing or counted twice")
        division_parents.add(parent)
        require(set(division["daughter_cell_ids"]) == set(children[parent]) and
                len(division["daughter_cell_ids"]) == 2 and
                rational(division["time"]) == rational(cells[parent]["stop_time"]),
                "Division identity/time/daughters disagree")
    require(division_parents == {cid for cid, x in cells.items() if x["stop_reason"] == "division"},
            "Observed division ledger is incomplete")

    def descends(cell, ancestor):
        while cell is not None:
            if cell == ancestor:
                return True
            cell = cells[cell]["parent_cell_id"]
        return False

    truth = ledger["synthetic_truth_only"]
    truth_map = {item["variant_tag"]: item["new_origin_segment"] for item in truth}
    require(len(truth_map) == len(truth) and
            all(k.startswith("TOY_") and v in cells for k, v in truth_map.items()),
            "Synthetic origin truth is not uniquely labeled")
    calls = ledger["variant_calls"]
    require(type(calls) is list and len(calls) <= MAX_RECORDS, "Call table outside supported domain")
    call_map = {}
    for call in calls:
        pair = (call["sample_id"], call["variant_tag"])
        require(pair not in call_map and pair[0] in samples and pair[1] in truth_map and
                call["call_state"] in CALLS and
                call["molecular_truth_is_known_only_in_simulation"] is True,
                "Call identity, state or provenance invalid")
        call_map[pair] = call["call_state"]
        if call["call_state"] != "unknown":
            carrier = descends(samples[pair[0]], truth_map[pair[1]])
            require(carrier == (call["call_state"] == "toy_validated_alternate"),
                    "Toy call contradicts the explicit inherited-carrier truth")
    require(set(call_map) == {(sample, variant) for sample in samples for variant in truth_map},
            "Missing target calls need explicit unknown rows, never implicit reference")
    variants_assigned = set()
    admitted, leaf_ambiguous, alternate_copies, unknown_calls = [], [], 0, 0
    for assignment in assignments.values():
        tag = assignment["variant_tag"]
        require(tag in truth_map and tag not in variants_assigned, "Variant origin counted twice")
        variants_assigned.add(tag)
        require(assignment["actual_route_label"] is None and
                assignment["molecular_event_time_observed_exactly"] is False,
                "Actual routing or exact event time is not admitted")
        positives = [samples[s] for s in samples
                     if call_map[s, tag] == "toy_validated_alternate"]
        negatives = [samples[s] for s in samples
                     if call_map[s, tag] == "toy_validated_reference"]
        alternate_copies += len(positives)
        unknown_calls += sum(call_map[s, tag] == "unknown" for s in samples)
        segment = assignment["assigned_cell_segment_id"]
        if assignment["classification"] == "toy_branch_supported_interval":
            require(segment in cells and len(positives) >= 2 and
                    all(descends(x, segment) for x in positives) and
                    all(not descends(x, segment) for x in negatives) and len(negatives) >= 1,
                    "Toy branch support/outgroup requirement not met")
            window = assignment["origin_time_window"]
            require(type(window) is list and len(window) == 2 and
                    rational(cells[segment]["birth_time"]) <= rational(window[0]) <
                    rational(window[1]) <= rational(cells[segment]["stop_time"]),
                    "Origin interval exceeds its tracked segment")
            admitted.append(tag)
        elif assignment["classification"] == "leaf_ambiguous_not_an_admitted_origin":
            require(len(positives) == 1 and segment is None and
                    assignment["origin_time_window"] is None,
                    "Leaf-only evidence cannot carry a resolved new-origin assignment")
            leaf_ambiguous.append(tag)
        else:
            raise ValueError("Unsupported origin-assignment classification")
    require(variants_assigned == set(truth_map), "Origin assessment missing")
    stage_counts = {stage: sum(cell["stages"][stage] for cell in cells.values()) for stage in STAGES}
    return {
        "status": "passed_synthetic_ledger_integrity_only",
        "tracked_cells": len(cells), "observed_divisions": len(divisions),
        "tracked_cell_time": str(sum(rational(x["stop_time"])-rational(x["birth_time"])
                                    for x in cells.values())),
        "time_unit": ledger["time_unit"], "collection_stages": stage_counts,
        "dead_terminal_cells": sum(x["stop_reason"] == "death" for x in cells.values()),
        "lost_tracking_terminal_cells": sum(x["stop_reason"] == "lost_tracking" for x in cells.values()),
        "unsequenced_terminal_genotypes_unknown": sum(
            x["stop_reason"] != "division" and not x["stages"]["sequenced"]
            for x in cells.values()),
        "culture_records": len(cultures),
        "same_founder_samples_are_nested_not_independent_origins": True,
        "toy_validated_alternate_descendant_copies": alternate_copies,
        "toy_branch_supported_variant_tags": admitted,
        "leaf_ambiguous_variant_tags": leaf_ambiguous,
        "explicit_unknown_target_calls": unknown_calls,
        "synthetic_true_origins": len(truth_map),
        "true_origin_count_available_only_from_simulation": True,
        "cell_stage_fraction_is_event_inclusion_probability": False,
        "actual_study_fields_resolved": 0, "biological_panel_admitted": False,
        "event_inclusion_or_count_law_estimated": False,
    }


def verify_source(path):
    runtime_guard()
    source = load_json(BASE/"SOURCE_LEDGER.json")["primary"]
    if path is None or not Path(path).is_file():
        return {"status": "UNRUN_cached_primary_not_supplied", "new_requests": 0,
                "raw_source_redistributed": False}
    data = Path(path).read_bytes()
    require(len(data) == source["raw_xml_bytes"] and
            hashlib.sha256(data).hexdigest() == source["raw_xml_sha256"],
            "Cached primary bytes differ")
    tree = ET.fromstring(data)
    article = tree if tree.tag == "article" else tree.find("article")
    require(article is not None, "One primary article is required")
    text = lambda element: " ".join("".join(element.itertext()).split()) if element is not None else ""
    require(text(article.find("front/article-meta/title-group/article-title")) == source["title"],
            "Primary title changed")
    for kind, expected in (("doi", source["doi"]), ("pmid", source["pmid"]),
                           ("pmcid", source["pmcid"])):
        require(text(article.find('front/article-meta/article-id[@pub-id-type="'+kind+'"]')) == expected,
                "Primary identifier changed")
    permissions = text(article.find("front/article-meta/permissions"))
    require("Attribution 4.0 International" in permissions and
            "creativecommons.org/licenses/by/4.0/" in permissions, "Source license missing")
    paragraphs = [text(x) for x in article.findall("body//p")]
    require(len(paragraphs) == source["body_paragraph_count"], "Primary paragraph inventory changed")
    for anchor in source["verified_anchors"]:
        require(hashlib.sha256(paragraphs[anchor["body_paragraph_index"]].encode()).hexdigest() ==
                anchor["normalized_paragraph_sha256"], "Source paragraph anchor changed")
    matrix = load_json(BASE/"REQUIREMENT_MATRIX.json")
    indices = {x["body_paragraph_index"] for x in source["verified_anchors"]}
    require(all(set(row["primary_paragraph_anchors"]) <= indices and
                row["candidate_requirement_status"] == "unresolved"
                for row in matrix["requirements"]), "Requirement source/admission mapping invalid")
    return {"status": "passed_cached_primary_and_requirement_anchors",
            "new_requests": 0, "source_sha256": source["raw_xml_sha256"],
            "source_bytes": len(data), "normalized_anchors_verified": len(indices),
            "requirement_rows": len(matrix["requirements"]),
            "source_metadata_checks": 5, "raw_source_redistributed": False,
            "source_likelihood_or_software_replayed": False}


def producer_checks(ledger, rules, digest):
    runtime_guard()
    summary = verify_ledger(ledger, rules, digest)
    checks = 0
    def check(condition):
        nonlocal checks
        require(condition, "Independent-ready producer benchmark failed")
        checks += 1
    check(summary["tracked_cells"] == 13 and summary["observed_divisions"] == 6)
    check(summary["tracked_cell_time"] == "20")
    check(summary["collection_stages"] == dict(zip(STAGES, (5, 4, 3, 3))))
    check(summary["dead_terminal_cells"] == summary["lost_tracking_terminal_cells"] == 1)
    check(summary["unsequenced_terminal_genotypes_unknown"] == 4)
    check(summary["toy_validated_alternate_descendant_copies"] == 3 and
          summary["toy_branch_supported_variant_tags"] == ["TOY_VARIANT_A"] and
          summary["leaf_ambiguous_variant_tags"] == ["TOY_VARIANT_B"])
    check(summary["synthetic_true_origins"] == 2 and not summary["biological_panel_admitted"])
    invalid = []
    def changed(path, value):
        result = copy.deepcopy(ledger)
        node = result
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        return result
    invalid.extend([
        changed(("provenance",), "observed"),
        changed(("design_status", "actual_registry_fields_resolved"), 1),
        changed(("design_status", "actual_axis"), [1, 0, -1]),
        changed(("binomial_or_poisson_count_law_admitted",), True),
        changed(("cells", 8, "stages", "outgrown"), True),
        changed(("cells", 9, "stages", "available_at_collection"), True),
        changed(("cells", 4, "unknown_genotype_is_a_negative_call"), True),
        changed(("cells", 4, "parent_cell_id"), "B"),
        changed(("cells", 0, "parent_cell_id"), "A"),
        changed(("divisions", 0, "daughter_cell_ids"), ["A", "A"]),
        changed(("cells", 4, "sample_id"), "S21"),
        changed(("variant_calls",), ledger["variant_calls"][:-1]),
        changed(("origin_assignments",), ledger["origin_assignments"]+[ledger["origin_assignments"][0]]),
        changed(("origin_assignments", 0, "origin_time_window"), ["0", "6"]),
        changed(("origin_assignments", 0, "molecular_event_time_observed_exactly"), True),
        changed(("origin_assignments", 0, "actual_route_label"), "R1"),
        changed(("origin_assignments", 1, "classification"), "toy_branch_supported_interval"),
        changed(("toy_rules_sha256",), "0"*64),
    ])
    for value in invalid:
        try:
            verify_ledger(value, rules, digest)
        except (ValueError, TypeError, KeyError):
            checks += 1
        else:
            raise ValueError("Inconsistent synthetic ledger accepted")
    # An explicit unknown call remains distinguishable from a negative, rather
    # than being silently dropped. This case loses branch admission and declines.
    unknown = copy.deepcopy(ledger)
    unknown["variant_calls"][0]["call_state"] = "unknown"
    try:
        verify_ledger(unknown, rules, digest)
    except ValueError:
        checks += 1
    else:
        raise ValueError("Unresolved carrier evidence retained false branch admission")
    return {"status": "passed_producer_semantic_checks", "check_count": checks,
            "synthetic_summary": summary, "independent_review_status": "pending_root_review",
            "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "provenance": "SYNTHETIC", "event_probabilities_or_rates_estimated": False}


def main():
    runtime_guard()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-xml", type=Path)
    parser.add_argument("--outdir", type=Path, default=BASE)
    args = parser.parse_args()
    rules = load_json(BASE/"TOY_RULES.json")
    digest = hashlib.sha256((BASE/"TOY_RULES.json").read_bytes()).hexdigest()
    ledger = load_json(BASE/"SYNTHETIC_LEDGER.json")
    semantic = producer_checks(ledger, rules, digest)
    source = verify_source(args.primary_xml)
    args.outdir.mkdir(parents=True, exist_ok=True)
    for name, value in (("SEMANTIC_CHECK_RECEIPT.json", semantic),
                        ("SOURCE_VERIFICATION_RECEIPT.json", source)):
        (args.outdir/name).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"semantic_status": semantic["status"],
                      "semantic_checks": semantic["check_count"], "source": source,
                      "validator_sha256": semantic["validator_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
