"""Join the original 75-leaf roster and the published minimum-completion cells to sequence archive identifiers."""
import argparse
import csv
import json
from pathlib import Path
from urllib.request import urlopen
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
HISTORICAL = Path("research/leaf_lineages")
NCBI = "https://www.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new?acc="
TARGET = "DHQ1_B1-1-L1"


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def crosswalk(historical, identifiers):
    archive = read_rows(identifiers)
    roster = {r["sample_id"]: r for r in read_rows(historical / "carrier/sample_roster.tsv")}
    runs = {r["sample_alias"]: r for r in archive}
    assert len(archive) == len(runs) == len(roster) == 75 and runs.keys() == roster.keys()
    for field in ("experiment_accession", "sample_accession", "run_accession"):
        assert len({r[field] for r in archive}) == 75, field
    assert all(r["library_name"] == r["sample_alias"] for r in archive)

    variants = read_rows(historical / "carrier/carriers.tsv")
    sites = {f"{r['chromosome']}:{r['position']}": r for r in variants}
    common = json.loads((historical / "completion/orientation_result.json").read_text())
    candidates = []
    for site, leaves in common["unrestricted"]["additions_common_to_all_optima"].items():
        variant = sites[site]
        for leaf in leaves:
            assert leaf not in variant["listed_leaves"].split(";")
            candidates.append({
                "site": site, "change": variant["change"], "sample": leaf,
                "run": runs[leaf]["run_accession"],
                "biosample": runs[leaf]["sample_accession"],
            })
    assert len(candidates) == 10
    return {
        "matched_original_leaf_samples": len(runs),
        "unique_runs_among_ten_common_additions": len({x["run"] for x in candidates}),
        "distinct_sites_among_ten_common_additions": len(common["unrestricted"]["additions_common_to_all_optima"]),
        "named_target": {
            **runs[TARGET],
            "reported_genome_wide_mapped_depth": float(roster[TARGET]["mapped_depth"]),
            "reported_percent_genome_at_five_reads": float(roster[TARGET]["genome_pct_depth_at_least_five"]),
        },
        "ten_hypothetical_additions": candidates,
    }


def verify_primary(result):
    labels = {(r["sample"], r["run"], r["biosample"]) for r in result["ten_hypothetical_additions"]}
    for sample, accession, biosample in sorted(labels):
        with urlopen(NCBI + accession, timeout=30) as response:
            bundle = ET.fromstring(response.read())
        run = bundle.find("RUN")
        member = run.find("Pool/Member")
        assert run.get("accession") == accession and member.get("sample_name") == sample
        assert member.findtext(".//EXTERNAL_ID[@namespace='BioSample']") == biosample
        assert bundle.findtext("EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_NAME") == sample
        if sample == TARGET:
            assert run.get("total_spots") == "50599581" and run.get("total_bases") == "15179874300"
            files = run.findall("SRAFiles/SRAFile")
            assert sorted(x.get("semantic_name") for x in files) == ["SRA Lite", "SRA Normalized", "fastq", "fastq"]
        print(f"Verified {sample} in {accession} at {biosample}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical", type=Path, default=HISTORICAL, help="Path to the 0.9.0 leaf_lineages directory")
    parser.add_argument("--verify-ncbi", action="store_true", help="Also reopen the seven small NCBI run metadata records")
    args = parser.parse_args()
    result = crosswalk(args.historical, HERE / "dhq1_identifiers.tsv")
    if args.verify_ncbi:
        verify_primary(result)
    else:
        print(json.dumps(result, indent=2))
