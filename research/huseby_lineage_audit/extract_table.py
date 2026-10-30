#!/usr/bin/env python3
"""Parse only the text representation of Huseby 2017 official supplement.
No downloads, dependencies, or source-author code execution.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-json', type=Path, required=True,
                    help='Externally obtained supplement parsed JSON (markdown and metadata)')
parser.add_argument('--article-json', type=Path, required=True,
                    help='Externally obtained main-article parsed JSON')
parser.add_argument('--output-dir', type=Path, required=True,
                    help='External directory for transcribed source table and original audit')
args = parser.parse_args()
base = args.output_dir
base.mkdir(parents=True, exist_ok=True)
source = args.source_json
article_file = args.article_json
supp = json.loads(source.read_text())
article = json.loads(article_file.read_text())
assert supp['metadata']['sourceURL'] == 'https://pmc.ncbi.nlm.nih.gov/articles/instance/5400412/bin/msx052_Supp.pdf'
section = supp["markdown"].split("**Table S6.**", 1)[1].split("**Table S7.**", 1)[0]
pattern = re.compile(r"^\|\s*(\d+)\s*/\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([0-9.]+)\s*\|\s*$", re.M)
records = [
    {"lineage": int(lineage), "isolate": int(isolate),
     "parC": mutation.strip(), "ciprofloxacin_mic_mg_per_L": mic}
    for lineage, isolate, mutation, mic in pattern.findall(section)
]
assert len(records) == 20
assert {(r["lineage"],r["isolate"]) for r in records} == {(l,i) for l in range(1,11) for i in (1,2)}
by_lineage = defaultdict(list)
for r in records:
    by_lineage[r["lineage"]].append(r)
positive = [r for r in records if r["parC"] != "-"]
allele_counts = Counter(r["parC"] for r in positive)
allele_lineages = {
    allele: sorted({r["lineage"] for r in positive if r["parC"] == allele})
    for allele in sorted(allele_counts)
}
positive_lineages = sorted({r["lineage"] for r in positive})
both_positive = sorted(l for l,rs in by_lineage.items() if all(r["parC"] != "-" for r in rs))
same_reported_allele = sorted(l for l,rs in by_lineage.items() if len({r["parC"] for r in rs}) == 1)
s80_positive = sum(r["parC"] in ("S80I", "S80R") for r in positive)
assert len(positive) == 18
assert len(positive_lineages) == 10
assert both_positive == [2,4,5,6,7,8,9,10]
assert same_reported_allele == [2,6]
assert s80_positive == 10
assert allele_lineages["S80I"] == [5,8,9]
assert "18/20" in article["markdown"]
assert "10/18" in article["markdown"]
assert "three independent lineages" in article["markdown"]
csv_path = base / "huseby2017_s6.csv"
with csv_path.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
audit = {
    "doi": "10.1093/molbev/msx052",
    "source_url": supp["metadata"]["sourceURL"],
    "article_url": article["metadata"]["sourceURL"],
    "retrieval": supp["metadata"],
    "representation_note": "These hashes identify saved Firecrawl parsed JSON representations, NOT original PDF bytes.",
    "source_json_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "article_json_sha256": hashlib.sha256(article_file.read_bytes()).hexdigest(),
    "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    "replicate_unit": "independently evolved lineage",
    "N_lineages": len(by_lineage),
    "isolates_per_lineage": 2,
    "N_isolates": len(records),
    "parC_positive_isolates": len(positive),
    "lineages_at_least_one_sampled_parC_mutant": positive_lineages,
    "lineages_both_sampled_isolates_parC_mutant": both_positive,
    "lineages_same_reported_parC_allele_both_isolates": same_reported_allele,
    "distinct_lineage_amino_acid_substitution_pairs": sum(len(v) for v in allele_lineages.values()),
    "parC_S80_mutant_isolates": s80_positive,
    "amino_acid_substitution_isolate_counts": dict(sorted(allele_counts.items())),
    "amino_acid_substitution_lineages": allele_lineages,
    "MIC_units": "mg/L, established by main-article S6-linked paragraph (table header omits units)",
    "limitations": [
        "Table S6 reports parC amino-acid calls; it is not a whole-genome mutation table.",
        "The inherited gyrA S83L allele is not a de novo hit.",
        "The two colonies per lineage are nested samples, not independent evolutionary replicates.",
        "A '-' means no parC mutation reported in that isolate; it is not a genome-wide negative.",
        "Identical parC calls do not establish full clonal identity.",
        "Partial whole-genome sequencing described for eight selected clones has no complete S6 row linkage."
    ]
}
audit_path = base / "huseby2017_s6_audit.json"
audit_path.write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps({"csv":str(csv_path),"audit":str(audit_path),"N":len(records),"positive_isolates":len(positive),"positive_lineages":len(positive_lineages),"both_positive_lineages":len(both_positive)}))

