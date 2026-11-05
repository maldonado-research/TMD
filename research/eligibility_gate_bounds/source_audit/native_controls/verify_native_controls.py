#!/usr/bin/env python3
"""Offline replay of three bounded native eligibility-gate source observations.

Only Python's standard library is used. No network, author code or assay is run.
The evidence concerns selected published material, not a literature-wide absence.
"""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


SOURCES = {
    "mcdonald2009": {
        "filename": "S03.md",
        "bytes": 110618,
        "sha256": "5b6b1c5cf23a7866a174493d12c3a6190db12babc21062ad28215b1d1cbc67c2",
        "representation": "cached Firecrawl markdown representation, not original publisher bytes",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2778958/",
        "doi": "10.1534/genetics.109.107110",
    },
    "lind2019": {
        "filename": "lind2019_pmc.xml",
        "bytes": 297863,
        "sha256": "38fd0408ef2b5e367aa1fe0307f160839bdc537e85fcd517a584d5177bcd6984",
        "representation": "cached full JATS XML; only main article sections inspected here",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6324874/",
        "doi": "10.7554/eLife.38822",
    },
}


def pinned(path, spec):
    data = path.read_bytes()
    if len(data) != spec["bytes"] or hashlib.sha256(data).hexdigest() != spec["sha256"]:
        raise ValueError(f"Source fingerprint mismatch: {path}")
    return data


def require(condition, message):
    if not condition:
        raise ValueError(message)


def section(root, id_):
    found = root.findall(f".//article/body//sec[@id='{id_}']")
    require(len(found) == 1, f"Expected exactly one main article section {id_}")
    return " ".join("".join(found[0].itertext()).split())


def find_line(text, phrase):
    found = [i for i, line in enumerate(text.splitlines(), 1) if phrase in line]
    require(len(found) == 1, f"Expected unique source anchor: {phrase}")
    return found[0]


def replay(mcdonald_path, lind_path):
    mc = pinned(mcdonald_path, SOURCES["mcdonald2009"]).decode("utf-8")
    root = ET.fromstring(pinned(lind_path, SOURCES["lind2019"]))
    spectrum = section(root, "s2-4")
    sampling = section(root, "s4-2")
    sequencing = section(root, "s4-3")
    counts = re.search(
        r"Of the (\d+) mutants, (\d+) harboured a mutation in wsp "
        r"\((\d+) mutants\), aws \((\d+) mutants\) or mws \((\d+) mutants\)",
        spectrum,
    )
    require(counts is not None, "Missing Lind spectrum counts")
    total, focal, wsp, aws, mws = map(int, counts.groups())
    require((total, focal, wsp, aws, mws) == (109, 105, 46, 41, 18), "Changed spectrum counts")
    require(focal == wsp + aws + mws, "Focal counts do not sum")
    require("The remaining four had mutations in previously described rare pathways (PFLU0085, PFLU0183)" in spectrum,
            "Missing explicit rare-pathway count and identities")
    require("One randomly chosen colony per independent culture with WS colony morphology" in sampling,
            "Missing phenotype-conditioned sampling statement")
    require("double deletions of aws/mws, wsp/mws or wsp/aws" in sampling,
            "Missing deletion-background context")
    require("Sanger sequencing" in sequencing and "genome sequencing" in sequencing,
            "Missing molecular identification methods")

    sws_line = find_line(mc, "A single WS genotype, **s** low **w** rinkly **s** preader")
    sws_paragraph = mc.splitlines()[sws_line - 1]
    require("SWS; PBR715" in sws_paragraph and "SM Δ _wsp_ Δ _aws_ Δ _mws_ (PBR716)" in sws_paragraph,
            "Missing SWS identity or triple-deletion parent")
    require("41 suppressor mutants" in sws_paragraph and "(pflu1349)" in sws_paragraph,
            "Missing selected-strain suppressor analysis")
    sws_truth_line = find_line(mc, "Deletion of _swsR_ from SWS caused the phenotype to revert")
    require("revealed no mutations" in mc.splitlines()[sws_truth_line - 1],
            "SWS causal molecular variant not preserved as unresolved")
    wsx_table_line = find_line(mc, "| WSX [_b_]")
    require("| ? | ? | ? |" in mc.splitlines()[wsx_table_line - 1], "WSX table uncertainty missing")
    wsx_footnote_line = find_line(mc, "Suppressor analysis implicates the _wsp_ locus (17 transposon insertions")
    wsx_discussion_line = find_line(mc, "WSX, the one WS genotype with no mutation")
    require("requires a functional Wsp pathway" in mc.splitlines()[wsx_discussion_line - 1],
            "WSX functional Wsp association missing")

    return {
        "schema_version": 1,
        "status": "PASS_CACHED_SOURCE_REPLAY",
        "scope": "McDonald 2009 selected cached passages and Lind 2019 main-article sections; no new acquisition",
        "sources": SOURCES,
        "observations": [
            {
                "id": "lind_selected_rare_routes",
                "source": "lind2019",
                "anchors": ["main article JATS sec[@id='s2-4']", "main article JATS sec[@id='s4-2']", "main article JATS sec[@id='s4-3']"],
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6324874/#s2-4",
                "selected_ws_mutants": total,
                "focal_wam_mutants": focal,
                "focal_route_counts": {"Wsp": wsp, "Aws": aws, "Mws": mws},
                "reported_rare_pathway_mutants": total - focal,
                "reported_rare_pathways": ["PFLU0085", "PFLU0183"],
                "derived_rare_fraction_among_sampled_ws_mutants": str(Fraction(total - focal, total)),
                "derived_wam_fraction_among_sampled_ws_mutants": str(Fraction(focal, total)),
                "selection": "One colony with WS morphology per independent culture; mixtures of genetic backgrounds include pathway double deletions.",
                "truth_procedure": "Candidate-gene Sanger sequencing; genome sequencing for a few candidates without identified focal mutations.",
                "interpretation": "Concrete non-focal biological routes occur within the selected WS-mutant collection. This conditional sample composition is not a false-entry probability for known-Other units.",
                "known_other_pre_gate_denominator": None,
                "independent_frozen_gate_outcomes": None,
                "admitted_as_native_beta_calibration": False,
            },
            {
                "id": "sws_triple_deletion",
                "source": "mcdonald2009",
                "anchor": "SWS: a wsp-, aws-, and mws-independent route to WS",
                "cached_markdown_lines": [sws_line, sws_truth_line],
                "selected_strain": "SWS PBR715",
                "parent": "SM Δwsp Δaws Δmws PBR716",
                "selected_strain_count": 1,
                "reported_suppressor_mutants": 41,
                "interpretation": "A WS phenotype can occur despite deletion of the three focal modules. Functional swsR dependence was demonstrated, while repeated sequencing did not identify its causal mutation. A selected strain and its suppressor mutants are not independent known-Other eligibility trials.",
                "known_other_pre_gate_denominator": None,
                "independent_frozen_gate_outcomes": None,
                "admitted_as_native_beta_calibration": False,
            },
            {
                "id": "wsx_unresolved",
                "source": "mcdonald2009",
                "anchors": ["Table 1 WSX row and footnote b", "Discussion WSX functional-dependency statement"],
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2778958/#tblfn2",
                "cached_markdown_lines": [wsx_table_line, wsx_footnote_line, wsx_discussion_line],
                "reported_wsp_suppressor_insertions": 17,
                "interpretation": "WSX lacks an identified mutation in the focal loci but depends functionally on Wsp; molecular uncertainty does not establish known-Other truth. Suppressor insertions are mechanistic observations, not independent negative-control trials.",
                "admitted_as_known_other_truth": False,
                "admitted_as_native_beta_calibration": False,
            },
        ],
        "numerical_native_beta": None,
        "source_body_redistributed": False,
        "new_network_requests": 0,
        "author_code_executed": False,
        "conclusion": "The inspected sources establish that a WS phenotype gate can admit non-focal routes; they do not supply a known-Other pre-gate denominator and independent frozen-gate outcome ledger for numerical native false-entry calibration.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcdonald-markdown", required=True, type=Path)
    parser.add_argument("--lind-jats", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = replay(args.mcdonald_markdown, args.lind_jats)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "observations": len(result["observations"]), "numerical_native_beta": None}))


if __name__ == "__main__":
    main()
