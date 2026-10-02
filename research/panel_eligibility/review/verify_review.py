#!/usr/bin/env python3
"""Offline primary-source review; no acquisition, inference, or output mutation by default.

Public ledgers and private XML caches can have different roots. Only the four
explicitly pinned XML files are read from --raw-source-root. This script checks
source content and sampling counts before checking the authors' eligibility flags.
Original review code: MIT under the TMD repository licensing terms.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


PINS = {
    "lind2019": ("lind_sun", "lind2019_pmc.xml", "10.7554/eLife.38822", "PMC6324874", "38fd0408ef2b5e367aa1fe0307f160839bdc537e85fcd517a584d5177bcd6984", 297863),
    "sun2023": ("lind_sun", "sun2023_pmc.xml", "10.1099/mic.0.001323", "PMC10268835", "6794652551e935e9f5b6ed53cd6b2d034b6b40a5acabeb4c614c39c75845192a", 180237),
    "Horton2025": ("hotspot", "horton_pmc.xml", "10.1093/molbev/msaf183", "PMC12344412", "38c5377591da67d47ccdef8cfb08f26348e2aef82b34ac69953c8ccef202fb40", 117119),
    "TorresAlonso2026": ("hotspot", "torres_pmc.xml", "10.1093/nar/gkag673", "PMC13335488", "05078a07b8098f25b9c393fdc66c9ac8959a24f86f69173ce93d6c72c9053c26", 206305),
}
PUBLIC_FILES = ["INDEPENDENT_REVIEW.md", "REVIEW_RECEIPT.json", "verify_review.py"]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(value):
    """Join XML itertext exactly, then collapse whitespace; no symbol rewriting."""
    if isinstance(value, ET.Element):
        value = "".join(value.itertext())
    return " ".join(value.split())


def walk_main(node):
    if node.tag in {"sub-article", "response"}:
        return
    yield node
    for child in node:
        yield from walk_main(child)


def text_at(index, locator):
    ident, *children = locator.split("/")
    check(ident in index, "Missing main-article XML ID: " + ident)
    node = index[ident]
    for child in children:
        node = node.find(child)
        check(node is not None, "Missing XML child: " + locator)
    return norm(node)


def phrase(index, locator, expected):
    text = text_at(index, locator)
    check(norm(expected) in text, "Primary-source phrase mismatch at " + locator + ": " + expected)
    return text


def match(pattern, text, message):
    found = re.search(pattern, text)
    check(found is not None, "Could not extract " + message)
    return found


def load_primary(raw_root):
    indices, identities = {}, []
    for study, (group, filename, doi, pmcid, digest, size) in PINS.items():
        data = (raw_root / group / "raw" / filename).read_bytes()
        check(sha(data) == digest and len(data) == size, "Source bytes/hash mismatch: " + study)
        root = ET.fromstring(data)
        article = root if root.tag == "article" else root.find("article")
        check(article is not None, "No top-level primary article: " + study)
        ids = {n.get("pub-id-type"): norm(n) for n in article.findall("./front/article-meta/article-id")}
        check(ids.get("doi") == doi and ids.get("pmcid") == pmcid, "Primary DOI/PMCID mismatch: " + study)
        check(ids.get("pmcid-ver") == pmcid + ".1", "Primary PMCID version mismatch: " + study)
        license_node = article.find("./front/article-meta/permissions/license")
        check(license_node is not None, "Missing article permissions: " + study)
        hrefs = [n.get("{http://www.w3.org/1999/xlink}href", "") for n in license_node.iter()]
        hrefs.extend(norm(n) for n in license_node.iter() if n.tag.endswith("}license_ref"))
        check(any("creativecommons.org/licenses/by/4.0" in href for href in hrefs), "Main-article CC BY 4.0 notice mismatch: " + study)
        index = {}
        for node in walk_main(article):
            ident = node.get("id")
            if ident:
                check(ident not in index, "Duplicate main-article ID: " + study + "/" + ident)
                index[ident] = node
        indices[study] = index
        identities.append(dict(study=study, doi=doi, pmcid=pmcid,
                               pmcid_version=ids["pmcid-ver"], sha256=digest,
                               bytes=size, main_article_license="CC BY 4.0"))
    return indices, identities


def primary_observations(ix):
    l, s, h, t = (ix[k] for k in ("lind2019", "sun2023", "Horton2025", "TorresAlonso2026"))
    spectrum = phrase(l, "s2-4", "The remaining four had mutations in previously described rare pathways (PFLU0085, PFLU0183)")
    total, focal = map(int, match(r"Of the (\d+) mutants, (\d+) harboured", spectrum, "Lind aggregate").groups())
    counts = {gene: int(match(rf"{gene} \((\d+) mutants\)", spectrum, "Lind " + gene).group(1)) for gene in ["wsp", "aws", "mws"]}
    check(counts == {"wsp": 46, "aws": 41, "mws": 18} and total == 109 and focal == sum(counts.values()) == 105 and total - focal == 4, "Lind aggregate/count arithmetic mismatch")
    phrase(l, "fig8/caption", "Only within operon comparisons are valid for this figure as the mutants isolated without selection had double deletions of the other operons.")
    methods = phrase(l, "s4-2", "One randomly chosen colony per independent culture with WS colony morphology was restreaked once on KB agar.")
    assay_cultures = int(match(r"(\d+) independent 110 μl cultures", methods, "Lind cultures per assay").group(1))
    check(assay_cultures == 60, "Lind per-assay culture count changed")
    phrase(l, "s4-2", "this method has only been shown to be valid in cases where total population size is not significantly different")
    caption = text_at(l, "fig2/caption")
    aws_wsp_n, mws_n, wt_n = map(int, match(r"n = (\d+) for Aws and Wsp, n = (\d+) for Mws, n = (\d+) for WT", caption, "Lind Figure 2 denominators").groups())
    check((aws_wsp_n, mws_n, wt_n) == (200, 400, 100), "Lind Figure 2 counts changed")
    rates = text_at(l, "s2-1")
    rate_patterns = {"Aws":r"Aws pathway \(([\d.]+) × 10−9\)", "Wsp":r"that of Wsp \(([\d.]+) × 10−9\)",
                     "Mws":r"Mws pathway \(([\d.]+) × 10−9\)", "WT":r"three pathways are intact \(([\d.]+) × 10−9\)"}
    extracted_rates = {route: float(match(pattern, rates, "Lind " + route + " rate").group(1)) * 1e-9 for route, pattern in rate_patterns.items()}
    for route, mantissa in {"Wsp":3.7,"Aws":6.5,"Mws":0.74,"WT":11.2}.items():
        check(abs(extracted_rates[route] / (mantissa*1e-9) - 1) < 1e-14, "Lind mutation rate extraction mismatch: " + route)
    for assertion in ["PBR721 carries the Wsp pathway but is devoid of Aws and Mws", "PBR713 carries the Aws pathway but is devoid of Wsp and Mws", "PBR712 harbours the Mws pathway but is devoid of Wsp and Aws"]:
        check(assertion in rates, "Lind strain-route mapping changed")
    historical = match(r"most commonly used \((\d+)/(\d+)\) under selection", text_at(l, "s2-7"), "historical Wsp fraction")
    check(tuple(map(int, historical.groups())) == (15, 24), "Historical Wsp comparison changed")
    phrase(l, "s4-4", "Competitions were performed in independently inoculated quadruplicates")
    phrase(l, "s4-4", "microcosms with >5% smooth colonies were excluded (two cases)")
    phrase(l, "s4-4", "Control competitions were also used to determine the cost of the double deletions and the reporter construct")
    phrase(s, "s6", "We only use experimental data published previously, described in Appendix B.")
    phrase(s, "s8-2", "It is not a statement about the true number of WS mutations per gene")
    phrase(s, "s8-3", "We used the experimental data for the aws pathway in Appendix B (Table 3) to calibrate the log-normal DMR model.")
    ref = ix["sun2023"]["R21"].find(".//pub-id[@pub-id-type='doi']")
    check(ref is not None and norm(ref) == PINS["lind2019"][2], "Sun empirical-data reference is not Lind DOI")
    aws_rows, current_gene = [], None
    for tr in s["T3"].findall("./table/tbody/tr"):
        cells = [norm(td) for td in tr.findall("td")]
        if not cells or cells[0] == "Total":
            continue
        if cells[0].startswith("aws"):
            current_gene = cells.pop(0)
        check(current_gene is not None and len(cells) >= 2, "Sun Table 3 structure changed")
        aws_rows.append(dict(gene=current_gene, mutation=cells[0], reported_occurrences=int(cells[1])))
    check(len(aws_rows) == 12 and sum(row["reported_occurrences"] for row in aws_rows) == 41, "Sun Table 3 count mismatch")
    targets = []
    for tr in s["T2"].findall("./table/tbody/tr"):
        cells = [norm(td) for td in tr.findall("td")]
        if cells and cells[0] != "Total":
            targets.append(int(cells[1]))
    check(len(targets) == 16 and sum(targets) == 500, "Sun estimated-target inventory changed")
    f1 = text_at(h, "msaf183-F1/caption")
    f1_counts = [int(x) for x in re.findall(r"\(n = (\d+)\)", f1)]
    f1_total = int(match(r"Total sequenced replicates = (\d+)", f1, "Horton Figure 1 total").group(1))
    check(f1_counts == [29, 112, 434, 47] and sum(f1_counts) == f1_total == 622, "Horton Figure 1 counts mismatch")
    f5 = text_at(h, "msaf183-F5/caption")
    seeded = list(map(int, match(r"independent replicates \(n = (\d+), (\d+), (\d+), and (\d+) respectively\)", f5, "Horton seeded populations").groups()))
    evolved = list(map(int, match(r"Sanger sequencing of the ntrB locus \(n = (\d+), (\d+), (\d+), and (\d+)\)", f5, "Horton evolved populations").groups()))
    check(seeded == [49, 52, 52, 51] and evolved == [38, 43, 44, 19], "Horton Figure 5 counts mismatch")
    phrase(h, "msaf183-s4.5", "monitored daily for emergence of motility zones")
    phrase(h, "msaf183-s4.5", "The first motile zone to appear per plate was passaged within 24 h")
    phrase(h, "msaf183-s4.5", "the mutation may have appeared during the initial growth of the colony.")
    phrase(h, "msaf183-s2.1", "We assessed hotspot potency by measuring the proportion of independent replicates")
    phrase(h, "msaf183-s4.6", "divided by the number of such sites per genome")
    phrase(h, "msaf183-s4.7", "Fold-changes in potency were calculated using Fisher's exact test's odds ratio")
    tor = phrase(t, "SEC2-5", "Thirty independent cultures per strain")
    phrase(t, "SEC2-5", "Cells (50 ml) were harvested")
    phrase(t, "SEC2-5", "expressed as the ratio of RifR colonies to total viable cells.")
    phrase(t, "SEC2-5", "For each strain and condition, at least 10 independent RifR colonies were analysed.")
    for ident in ["F2", "F3", "F4", "F5"]:
        phrase(t, ident + "/caption", "A 10-ml aliquot of each culture")
        phrase(t, ident + "/caption", "RifR CFUs normalised to total CFUs obtained on LB from untreated cells.")
        phrase(t, ident + "/caption", "at least five independent experiments")
    phrase(t, "SEC3-24", "The fitness costs of these mutations were not assessed;")
    return dict(lind_total=total, lind_focal_counts=counts, lind_rare_aggregate=total-focal,
                lind_cultures_per_assay=assay_cultures,
                lind_figure2_n=dict(Wsp=aws_wsp_n, Aws=aws_wsp_n, Mws=mws_n, WT=wt_n),
                lind_reported_mutation_rates=extracted_rates,
                historical_Wsp_fraction=dict(numerator=15, denominator=24, archive_17_6_3_equivalence_authenticated=False),
                sun_table3_rows=aws_rows, sun_table3_total=41, sun_new_biological_cohorts=0,
                sun_estimated_target_genes=len(targets), sun_estimated_targets_total=sum(targets),
                horton_figure1_group_n=f1_counts, horton_figure1_total=f1_total,
                horton_figure5_seeded=seeded, horton_figure5_evolved_sequenced=evolved,
                horton_figure5_nonemergent_derived=[a-b for a,b in zip(seeded,evolved)],
                torres_methods_cultures=30, torres_caption_experiments_lower_bound=5,
                torres_methods_harvest_ml=50, torres_caption_treated_aliquot_ml=10,
                torres_sequenced_colonies_per_strain_condition_lower_bound=10,
                torres_fitness_costs_assessed=False)


def verify_ledgers(ledger_root, ix, obs):
    reviewed = []
    def read(relative):
        data = (ledger_root / relative).read_bytes()
        reviewed.append(dict(path=relative, sha256=sha(data)))
        return json.loads(data)
    ls = read("lind_sun/ELIGIBILITY_ROWS.json")
    hot = read("hotspot/ELIGIBILITY_LEDGER.json")
    lrows = {r["row_id"]: r for r in ls["rows"]}
    hrows = {r["row_id"]: r for r in hot["observation_rows"]}
    check(len(lrows) == len(ls["rows"]) == 14 and len(hrows) == len(hot["observation_rows"]) == 6, "Duplicate or changed ledger row IDs/counts")
    for route, gene in [("Wsp", "wsp"), ("Aws", "aws"), ("Mws", "mws")]:
        check(lrows["L2019_spectrum_" + route]["reported_n"] == obs["lind_focal_counts"][gene], "Lind ledger spectrum mismatch: " + route)
        check(lrows["L2019_rate_" + route]["reported_n"] == obs["lind_figure2_n"][route], "Lind ledger rate denominator mismatch: " + route)
        check("double" in lrows["L2019_spectrum_" + route]["reason"].lower() or "deleted" in lrows["L2019_spectrum_" + route]["reason"].lower(), "Lind spectrum background qualification missing")
        expected_rate = obs["lind_reported_mutation_rates"][route]
        check(abs(lrows["L2019_rate_" + route]["reported_mutation_rate"] / expected_rate - 1) < 1e-14, "Lind rate ledger mismatch: " + route)
    for row_id, count in {"L2019_rare_aggregate":4, "L2019_preselection_aggregate":109, "L2019_WT_total_rate":100, "L2019_selected_historical_comparison":24, "L2019_fitness_competitions":4, "S2023_aws_reuse":41, "S2023_GPM_estimates":500}.items():
        check(lrows[row_id]["reported_n"] == count, "Lind/Sun count mismatch: " + row_id)
    check(lrows["L2019_WT_total_rate"]["reported_mutation_rate"] == 11.2e-9, "Lind WT rate mismatch")
    check("15/24" in lrows["L2019_selected_historical_comparison"]["route"], "Historical selected fraction missing")
    check("published experiments" in lrows["S2023_aws_reuse"]["reason"] and "independent replication" in lrows["S2023_aws_reuse"]["reason"], "Sun reuse qualification missing")
    for row in lrows.values():
        study = row["study"]
        check(row["doi"] == PINS[study][2], "Ledger source DOI mismatch")
        for locator in row["source_locators"]:
            text_at(ix[study], locator)
        for field in ["matched_baseline_counts", "matched_selected_route_counts", "fixed_route_control_introduced", "fixed_route_control_recovered"]:
            check(row[field] is None, "Missing target observation was encoded as data: " + row["row_id"] + "/" + field)
        check(row["eligible_for_matched_tmd_panel"] is False, "Eligibility flag disagrees with independently checked observation units")
    timing = hrows["HOT-HOR-TIMING"]["exact_denominators_and_unresolved_mapping"]
    for field, observed in [("seeded",obs["horton_figure5_seeded"]),("evolved_sequenced",obs["horton_figure5_evolved_sequenced"]),("not_evolved_by_day8",obs["horton_figure5_nonemergent_derived"])]:
        check(timing[field] == observed, "Horton timing ledger count mismatch: " + field)
    check("Derived" in timing["not_evolved_by_day8_provenance"], "Nonemergence subtraction mislabeled as raw failures")
    selected = hrows["HOT-HOR-SELECTED"]["exact_denominators_and_unresolved_mapping"]["available"]
    compact = re.sub(r"\s", "", selected)
    check("[29,112,434,47]" in compact and "622" in compact, "Horton Figure 1 ledger counts missing")
    check("per division" in hrows["HOT-HOR-SELECTED"]["context_matched_independent_WAM_mutation_supply"]["available"], "Horton supply-unit qualification missing")
    tor_freq = json.dumps(hrows["HOT-TOR-FREQUENCY"], ensure_ascii=False)
    for qualifier in ["30", "≥5", "50mL", "10mL", "untreated", "per-division"]:
        check(qualifier in tor_freq, "Torres hierarchy/denominator qualification missing: " + qualifier)
    check("culture-to-colony" in hrows["HOT-TOR-SPECTRUM"]["independent_cultures_or_populations"]["limitation"], "Torres culture-colony mapping qualification missing")
    for row in hrows.values():
        for locator in row["primary_xml_anchors"]:
            text_at(ix[row["source_id"]], locator)
        check("Current restricted matched" in row["eligibility_scope"], "Hotspot eligibility scope not restricted")
        check(row["current_matched_WAM_ledger_admitted"] is False, "Hotspot eligibility disagrees with checked assay units")
    check(hot["matched_WAM_ledger_admitted_count"] == 0 and hot["first_successful_arrival_observations_admitted_count"] == 0, "Hotspot admitted totals mismatch")
    check(ls["panel_test_performed"] is False and ls["source_workbooks_inspected"] is False, "Lind/Sun overstates execution or inspection")
    check("Wsp/Aws/Mws" in ls.get("eligibility_scope", "") and "inspected" in ls["eligibility_scope"].lower(), "Lind/Sun eligibility flags lack current-estimand/inspection scope")
    sm = read("lind_sun/SOURCE_MANIFEST.json")
    for source in sm["primary_sources"]:
        pin = PINS[source["study"]]
        check((source["doi"],source["pmcid"],source["sha256"],source["bytes"]) == (pin[2],pin[3],pin[4],pin[5]), "Lind/Sun source manifest mismatch")
        check(source["raw_publication_allowed_by_bundle"] is False, "Raw primary publication allowed unexpectedly")
    hs = read("hotspot/SOURCES.json")
    for source in hs["sources"]:
        pin = PINS[source["source_id"]]
        check((source["doi"],source["pmcid"],source["raw_primary_sha256"]) == (pin[2],pin[3],pin[4]), "Hotspot source manifest mismatch")
    excerpt_count = 0
    for group, filename, key in [("hotspot", "SOURCE_SUPPORT.json", "support"), ("lind_sun", "EVIDENCE_EXCERPTS.json", "rows")]:
        doc = read(group + "/" + filename)
        for entry in doc[key]:
            study = entry.get("source_id", entry.get("study"))
            pin = PINS[study]
            check(entry["doi"] == pin[2], "Excerpt attribution DOI mismatch")
            digest = entry.get("input_sha256", entry.get("source_sha256"))
            check(digest == pin[4], "Excerpt attribution hash mismatch")
            if "pmcid" in entry:
                check(entry["pmcid"] == pin[3], "Excerpt PMCID attribution mismatch")
            locator = entry.get("xml_element_id", entry.get("xml_locator"))
            excerpt = entry.get("short_attributed_excerpt", entry.get("evidence_excerpt"))
            phrase(ix[study], locator, excerpt)
            excerpt_count += 1
    transcribed_path = "lind_sun/sun_aws_table3_transcription.csv"
    data = (ledger_root / transcribed_path).read_bytes()
    reviewed.append(dict(path=transcribed_path, sha256=sha(data)))
    csv_rows = list(csv.DictReader(data.decode().splitlines()))
    check([{k: (int(row[k]) if k == "reported_occurrences" else row[k]) for k in ["gene","mutation","reported_occurrences"]} for row in csv_rows] == obs["sun_table3_rows"], "Sun attributed table transcription differs from primary Table 3")
    acquisitions = [read(g + "/ACQUISITION_STATUS.json") for g in ["hotspot", "lind_sun"]]
    check(sum(a["acquisitions_attempted"] if "acquisitions_attempted" in a else a["new_acquisition_attempts"] for a in acquisitions) == 11, "Acquisition attempt boundary changed")
    check(sum(a["downloaded_bytes"] for a in acquisitions) == 851374, "Acquisition byte boundary changed")
    missing = read("lind_sun/MISSING_MEASUREMENTS.json")
    pairs = {(row["study"],row["component"]) for row in missing["rows"]}
    expected_components = {"common_background", "context_matched_supply", "selected_route_counts", "independent_culture_lineage", "fixed_route_recovery_controls", "whole_context_holdout"}
    check(pairs == {(study,component) for study in ["lind2019","sun2023"] for component in expected_components} and len(missing["rows"]) == 12, "Missing-measurement coverage changed")
    public_count, checksum_count = 0, 0
    for group in ["hotspot", "lind_sun"]:
        whitelist = read(group + "/PUBLIC_FILES.json")
        entries = whitelist["files"]
        names = [entry if isinstance(entry,str) else entry["path"] for entry in entries]
        check(len(names) == len(set(names)), "Duplicate public whitelist paths")
        check(all(len(Path(name).parts) == 1 and name not in {"raw", ".", ".."} for name in names), "Unsafe public whitelist path")
        sums_data = (ledger_root / group / "SHA256SUMS.txt").read_bytes()
        reviewed.append(dict(path=group + "/SHA256SUMS.txt", sha256=sha(sums_data)))
        sums = {}
        for line in sums_data.decode().splitlines():
            found = match(r"([0-9a-f]{64})  (.+)$", line, "public checksum row")
            digest, name = found.groups()
            check(name not in sums, "Duplicate public checksum path")
            sums[name] = digest
        check(set(sums) == set(names) - {"SHA256SUMS.txt"}, "Public whitelist/checksum membership disagrees")
        for name in names:
            data = (ledger_root / group / name).read_bytes()
            digest = sha(data)
            if name != "SHA256SUMS.txt":
                check(digest == sums[name], "Public artifact checksum mismatch: " + group + "/" + name)
                checksum_count += 1
            reviewed.append(dict(path=group + "/" + name, sha256=digest))
            public_count += 1
    check(public_count == 24 and checksum_count == 22, "Public source-author artifact count changed")
    if (ledger_root / "README.md").is_file():
        data = (ledger_root / "README.md").read_bytes()
        historical_present = b"15/24" in data or b"15 Wsp mutants among 24" in data
        archive_present = any(value in data for value in [b"17/6/3", b"17,6,3", b"17, 6, 3"])
        check(b"not a systematic literature review" in data and archive_present and historical_present, "Combined report scope/historical-count warning missing")
        reviewed.append(dict(path="README.md", sha256=sha(data)))
    reviewed = [dict(path=path, sha256=digest) for path,digest in sorted({item["path"]:item["sha256"] for item in reviewed}.items())]
    return reviewed, dict(primary_sources=4, ledger_rows=20, checked_short_excerpts=excerpt_count,
                         authenticated_matched_panel_rows=0, tmd_hypothesis_tests=0,
                         source_author_public_files=public_count, source_author_checksum_entries=checksum_count,
                         missing_measurement_rows=12,
                         acquisition_attempts_total=11, acquired_bytes_total=851374)


def negative_self_checks(ledger_root, raw_root, ix, obs):
    """Exercise rejection paths in disposable copies; leave source files intact."""
    results = []
    def rejected(operation, expected, label):
        try:
            operation()
        except ValueError as error:
            check(expected in str(error), "Negative check failed at unexpected stage: " + str(error))
            results.append(label)
            return
        raise ValueError("Negative check incorrectly passed: " + label)
    with tempfile.TemporaryDirectory(prefix="negative_checks_", dir=Path(__file__).resolve().parent) as temporary:
        root = Path(temporary)
        for group in ["hotspot", "lind_sun"]:
            names = json.loads((ledger_root/group/"PUBLIC_FILES.json").read_text())["files"]
            (root/group).mkdir()
            for entry in names:
                name = entry if isinstance(entry,str) else entry["path"]
                shutil.copy2(ledger_root/group/name, root/group/name)
        path = root/"lind_sun/ELIGIBILITY_ROWS.json"
        original = path.read_bytes()
        data = json.loads(original)
        next(row for row in data["rows"] if row["row_id"] == "L2019_spectrum_Wsp")["reported_n"] = 47
        path.write_text(json.dumps(data))
        rejected(lambda: verify_ledgers(root,ix,obs), "spectrum mismatch", "changed_Lind_count_rejected")
        path.write_bytes(original)
        path = root/"hotspot/SOURCE_SUPPORT.json"
        original = path.read_bytes()
        data = json.loads(original)
        data["support"][0]["xml_element_id"] = "msaf183-F5"
        path.write_text(json.dumps(data))
        rejected(lambda: verify_ledgers(root,ix,obs), "phrase mismatch", "misattributed_excerpt_locator_rejected")
        path.write_bytes(original)
        path = root/"hotspot/NOTES.md"
        original = path.read_bytes()
        path.write_bytes(original+b"\nchanged\n")
        rejected(lambda: verify_ledgers(root,ix,obs), "checksum mismatch", "public_artifact_checksum_drift_rejected")
        path.write_bytes(original)
        for group,filename,*_ in PINS.values():
            (root/group/"raw").mkdir(exist_ok=True)
            shutil.copy2(raw_root/group/"raw"/filename,root/group/"raw"/filename)
        path = root/"lind_sun/raw/lind2019_pmc.xml"
        path.write_bytes(path.read_bytes()+b"\n")
        rejected(lambda: load_primary(root), "bytes/hash mismatch", "modified_primary_XML_bytes_rejected")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--raw-source-root", type=Path, help="Root containing hotspot/raw and lind_sun/raw; defaults to ledger root")
    parser.add_argument("--write-receipt", type=Path, help="Explicitly write a new review receipt; verification is read-only otherwise")
    parser.add_argument("--receipt", type=Path, help="Check reviewed ledger snapshot hashes against an existing receipt")
    parser.add_argument("--self-check", action="store_true", help="Exercise four rejection paths in disposable local copies")
    args = parser.parse_args()
    try:
        ix, identities = load_primary(args.raw_source_root or args.ledger_root)
        observations = primary_observations(ix)
        inputs, summary = verify_ledgers(args.ledger_root, ix, observations)
        negative_checks = negative_self_checks(args.ledger_root, args.raw_source_root or args.ledger_root, ix, observations) if args.self_check else []
        if args.receipt:
            prior = json.loads(args.receipt.read_text())
            check(prior["reviewed_ledger_inputs"] == inputs, "Reviewed ledger snapshot differs from receipt; rerun independent review before renewing receipt")
            check(prior["authenticated_primary_sources"] == identities and prior["observations"] == observations, "Receipt primary observations differ")
            check(prior["verifier_sha256"] == sha(Path(__file__).read_bytes()), "Verifier code differs from reviewed receipt")
        report = dict(schema="tmd-independent-primary-review-v1", round="R000002", review_date_utc="2026-10-02",
                      review_kind="independent_internal_primary_source_eligibility_review",
                      outcome="passed_with_scope_limits", external_peer_review=False,
                      raw_source_publication_allowed=False, public_files=PUBLIC_FILES,
                      verifier_sha256=sha(Path(__file__).read_bytes()),
                      authenticated_primary_sources=identities, reviewed_ledger_inputs=inputs,
                      observations=observations, verification_summary=summary,
                      negative_drift_checks_executed=negative_checks,
                      eligibility_scope="Inspected material for the current matched common-background context-specific Wsp/Aws/Mws supply-selected-outcome-fixed-route-recovery estimand only; no global dataset absence claim.",
                      statistical_significance_recomputed=False,
                      source_experiments_independently_reproduced=False,
                      scheduled_api_inference_tested=False)
        if args.write_receipt:
            args.write_receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(dict(outcome=report["outcome"], **summary), ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as error:
        print(json.dumps(dict(outcome="failed", error=str(error))), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
