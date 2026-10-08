"""Source-specific epithelial lineage stage audit; no variant/rate fitting."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

MAX_STAGE_COUNT = 1000000


def text(element):
    return " ".join("".join(element.itertext()).split()) if element is not None else ""


def stage_flow(available, isolated, outgrown, sequenced):
    """Descriptive nested counts, not independent Bernoulli capture trials."""
    values = (available, isolated, outgrown, sequenced)
    if any(type(value) is not int or not 0 <= value <= MAX_STAGE_COUNT for value in values):
        raise ValueError("stage counts must be integers0..1000000 excluding bool")
    if not available or not available >= isolated >= outgrown >= sequenced:
        raise ValueError("stage counts must have a positive available denominator and be nested")
    fraction = lambda numerator, denominator: str(Fraction(numerator, denominator)) if denominator else None
    return {"available_channel_cells": available, "isolated_cells": isolated,
            "outgrown_subclones": outgrown, "sequenced_subclones": sequenced,
            "realized_fraction_isolated_given_available": fraction(isolated, available),
            "realized_fraction_outgrown_given_isolated": fraction(outgrown, isolated),
            "realized_fraction_sequenced_given_outgrown": fraction(sequenced, outgrown),
            "realized_fraction_sequenced_given_available": fraction(sequenced, available),
            "not_isolated_count": available-isolated,
            "isolated_without_outgrowth_count": isolated-outgrown,
            "outgrown_not_sequenced_count": outgrown-sequenced,
            "available_denominator_is_not_all_cells_ever_born": True,
            "independent_capture_probability_or_interval_estimated": False}


def audit(article_file, software_files=None):
    if not __debug__:
        raise RuntimeError("Verification requires ordinary Python without -O/-OO")
    ledger = json.loads((Path(__file__).parent/"SOURCES.json").read_text())
    source = ledger["primary_source"]
    checks = {"source_byte_identity": 0, "source_metadata_and_license": 0,
              "normalized_source_anchors": 0, "stage_count_fields": 0,
              "realized_nested_flow_identities": 0, "invalid_stage_input_guards": 0,
              "cached_software_byte_and_identity_checks": 0}

    def check(condition, category):
        if not condition:
            raise ValueError("Source audit failed: " + category)
        checks[category] += 1

    data = article_file.read_bytes()
    check(len(data) == source["bytes"] and hashlib.sha256(data).hexdigest() == source["sha256"],
          "source_byte_identity")
    tree = ET.fromstring(data)
    article = tree if tree.tag == "article" else tree.find("article")
    if article is None:
        raise ValueError("Expected one primary article")
    check(text(article.find("front/article-meta/title-group/article-title")) == source["title"],
          "source_metadata_and_license")
    for identifier, expected in (("doi", source["doi"]), ("pmid", source["pmid"]), ("pmcid", source["pmc"])):
        value = text(article.find('front/article-meta/article-id[@pub-id-type="'+identifier+'"]'))
        check(value == expected, "source_metadata_and_license")
    permission = text(article.find("front/article-meta/permissions"))
    check("Attribution 4.0 International" in permission and "creativecommons.org/licenses/by/4.0/" in permission,
          "source_metadata_and_license")
    paragraphs = [text(element) for element in article.findall("body//p")]
    check(len(paragraphs) == source["body_paragraphs_inspected"], "source_metadata_and_license")
    for anchor in source["anchors"]:
        p = paragraphs[anchor["body_paragraph_index"]]
        check(hashlib.sha256(p.encode()).hexdigest() == anchor["normalized_paragraph_sha256"],
              "normalized_source_anchors")

    counts_text = paragraphs[47]
    ht = re.search(r"For HT115 lineage, we isolated (\d+) cells \(out of (\d+) cells in the channel\), of which (\d+) grew as subclonal cultures and were processed for sequencing", counts_text)
    rpe = re.search(r"For RPE1, we isolated (\d+) single cells \(out of (\d+) cells in the channel\), of which (\d+) grew as subclonal cultures", counts_text)
    sequenced_rpe = re.search(r"(Thirteen) of these subclonal cultures were processed for sequencing", counts_text)
    if ht is None or rpe is None or sequenced_rpe is None:
        raise ValueError("Source-specific stage-count prose changed")
    ht_i, ht_a, ht_g = map(int, ht.groups())
    rp_i, rp_a, rp_g = map(int, rpe.groups())
    rp_s = {"Thirteen": 13}[sequenced_rpe.group(1)]
    values = {"HT115": (ht_a, ht_i, ht_g, ht_g), "RPE1": (rp_a, rp_i, rp_g, rp_s)}
    expected = {"HT115": (45, 37, 11, 11), "RPE1": (26, 22, 15, 13)}
    flows = {}
    for name, counts in values.items():
        for actual, declared in zip(counts, expected[name]):
            check(actual == declared, "stage_count_fields")
        flows[name] = stage_flow(*counts)
        flow = flows[name]
        check(flow["not_isolated_count"]+flow["isolated_without_outgrowth_count"]+
              flow["outgrown_not_sequenced_count"]+flow["sequenced_subclones"] == flow["available_channel_cells"],
              "realized_nested_flow_identities")
        stages = [Fraction(flow[key]) for key in ("realized_fraction_isolated_given_available",
                  "realized_fraction_outgrown_given_isolated", "realized_fraction_sequenced_given_outgrown")]
        check(stages[0]*stages[1]*stages[2] == Fraction(flow["realized_fraction_sequenced_given_available"]),
              "realized_nested_flow_identities")
        check(all(0 <= fraction <= 1 for fraction in stages), "realized_nested_flow_identities")
        check(flow["sequenced_subclones"] <= flow["outgrown_subclones"] <= flow["isolated_cells"],
              "realized_nested_flow_identities")
    invalid = [(0, 0, 0, 0), (1, 2, 1, 1), (2, 1, 2, 1), (2, 2, 1, 2),
               (True, 1, 1, 1), (2, True, 1, 1), (2.0, 1, 1, 1), (-1, 0, 0, 0),
               (MAX_STAGE_COUNT+1, 1, 1, 1)]
    for counts in invalid:
        try:
            stage_flow(*counts)
        except (TypeError, ValueError):
            checks["invalid_stage_input_guards"] += 1
        else:
            raise ValueError("Invalid source stage input admitted")
    zero = stage_flow(1, 0, 0, 0)
    check(zero["realized_fraction_outgrown_given_isolated"] is None and
          zero["realized_fraction_sequenced_given_outgrown"] is None and
          zero["realized_fraction_sequenced_given_available"] == "0", "realized_nested_flow_identities")

    software = {"status": "unrun_software_cache_not_supplied", "notebooks_or_variants_executed": False}
    if software_files is not None:
        if len(software_files) != 3 or any(path is None or not path.is_file() for path in software_files):
            raise ValueError("All three software identity caches must be supplied together")
        commit_file, tree_file, readme_file = software_files
        pinned = ledger["pinned_software_identity"]
        for path, key in ((commit_file, "commit_response_sha256"), (tree_file, "tree_response_sha256"),
                          (readme_file, "readme_sha256")):
            check(hashlib.sha256(path.read_bytes()).hexdigest() == pinned[key],
                  "cached_software_byte_and_identity_checks")
        commit = json.loads(commit_file.read_text())[0]
        tree = json.loads(tree_file.read_text())
        check(commit["sha"] == pinned["commit_sha"], "cached_software_byte_and_identity_checks")
        if any(entry["mode"] != "100644" or entry["type"] != "blob" or "/" in entry["path"]
               for entry in tree["tree"]):
            raise ValueError("Expected the documented six-file flat Git tree")
        payload = b"".join(entry["mode"].encode()+b" "+entry["path"].encode()+b"\0"+
                           bytes.fromhex(entry["sha"]) for entry in tree["tree"])
        git_tree_hash = hashlib.sha1(b"tree "+str(len(payload)).encode()+b"\0"+payload).hexdigest()
        check(commit["commit"]["tree"]["sha"] == git_tree_hash == pinned["tree_sha"] and
              tree["sha"] == commit["sha"], "cached_software_byte_and_identity_checks")
        check(tree["truncated"] is False, "cached_software_byte_and_identity_checks")
        inventory = [{"path":entry["path"], "git_blob_sha1":entry["sha"], "size":entry["size"]}
                     for entry in tree["tree"]]
        check(inventory == pinned["tree_files"], "cached_software_byte_and_identity_checks")
        readme = readme_file.read_bytes()
        blob_hash = hashlib.sha1(b"blob "+str(len(readme)).encode()+b"\0"+readme).hexdigest()
        check(len(readme) == pinned["readme_bytes"] and blob_hash == pinned["readme_git_blob_sha1"],
              "cached_software_byte_and_identity_checks")
        check(b"Python 2.7" in readme, "cached_software_byte_and_identity_checks")
        software = {"status": "passed_pinned_metadata_and_README_identity", "commit_sha":commit["sha"],
                    "notebooks_or_variants_executed": False,
                    "software_reuse_license_established_by_article_license": False}

    return {"schema_version": 1, "status": "passed_source_stage_bookkeeping",
            "checks": checks, "check_total": sum(checks.values()), "stage_flows": flows,
            "primary_sequenced_subclones": ht_g+rp_s,
            "displayed_founder_lineages_per_background": 1,
            "additional_HT115_reference_subclone_is_a_matched_context_arm": False,
            "source_approximate_discussion_survival": {"HT115": "about30%", "RPE1": "about65%"},
            "approximate_discussion_survival_denominator_reconciled": False,
            "branch_call_RPE1_sensitivity_reported_results": "91.9%",
            "branch_call_RPE1_sensitivity_reported_methods": "91.8%",
            "last_decimal_detection_difference_reconciled": False,
            "method_call_sensitivity_is_absolute_cell_or_route_capture": False,
            "software_identity_replay": software,
            "lineage_mutation_variant_table_or_rate_likelihood_replayed": False,
            "matched_TMD_panel_admitted": False,
            "existing_actual_study_fields_resolved": 0,
            "cancer_prevention_or_clinical_effect": False,
            "new_theorem_or_priority_claim": False}


def main():
    if not __debug__:
        raise SystemExit("Verification requires ordinary Python without -O/-OO.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article-xml", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-against", type=Path)
    parser.add_argument("--pipeline-commit", type=Path)
    parser.add_argument("--pipeline-tree", type=Path)
    parser.add_argument("--pipeline-readme", type=Path)
    args = parser.parse_args()
    if args.article_xml is None or not args.article_xml.is_file():
        output = {"status": "unrun_source_cache_missing", "source_replay_passed": False,
                  "stage_count_or_mutation_rate_replayed": False}
    else:
        optional = (args.pipeline_commit, args.pipeline_tree, args.pipeline_readme)
        output = audit(args.article_xml, optional if any(optional) else None)
        if args.check_against and (json.dumps(output, indent=2)+"\n").encode() != args.check_against.read_bytes():
            raise SystemExit("Stored epithelial lineage stage audit differs")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({key: output.get(key) for key in ("status", "check_total", "checks")}))


if __name__ == "__main__":
    main()
