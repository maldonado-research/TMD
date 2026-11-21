"""Independently compare the native per-fruit variant calls with the deposited filtered table."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

from extract import read, TREES

VCF_SHA = {
    "angela": "972804d788f45e776177a269a631b2dfbda6bb0837c4575b9025a60fbc14225f",
    "sixto": "23b5d2ca1b11cd3549c83f8ef7c86c508bfa92dda383426945836dfa0eb8b36f",
}
TISSUES = dict(co="cotyledon", es="embryo sac", ec="endocarpe",
               ba="fruit base", nu="nucelle", pe="pericarpe")


def compare(path, table, sites, tree):
    n = Counter()
    seen = set()
    with gzip.open(path,"rt") as stream:
        for line in stream:
            if line.startswith("##"):
                continue
            c = line.rstrip().split("\t")
            if c[0] == "#CHROM":
                samples = c[9:]
                continue
            site = (int(c[0].split("_")[-1]), int(c[1]), c[3], c[4])
            if site not in sites:
                continue
            layout = c[8].split(":")
            for sample, genotype in zip(samples, c[9:], strict=True):
                species, branch, fruit, tissue = sample.split("_")
                assert species == tree
                key = (*site, branch, int(fruit), TISSUES[tissue])
                assert key in table and key not in seen
                seen.add(key)
                fields = dict(zip(layout, genotype.split(":")))
                ref, alt = map(int, fields["AD"].split(","))
                gt = fields["GT"]
                source_flag = int(gt in {"0|1", "0/1", "1/1", "1|1"})
                assert (ref, alt, int(fields["DP"]), source_flag) == table[key]
                n[gt] += 1
    assert seen == set(table)
    return {"fruit_marker_tissue_measurements": len(seen), "genotypes": dict(sorted(n.items()))}


def run(directory):
    rows = list(read(directory, "fruit_mutations.tsv.gz"))
    result = {}
    for species,(tree, prefix) in TREES.items():
        by_key = {}
        for r in rows:
            if r["species"] == species:
                key = (int(r["scaffold"]), int(r["position"]), r["normal"], r["mutation"],
                       r["branch"], int(r["fruit"]), r["tissue"])
                value = tuple(int(r[k]) for k in
                              ["normal_read_count","mutation_read_count","sequencing_depth","heterozygous_call_gatk"])
                assert key not in by_key or by_key[key] == value
                by_key[key] = value
        path = directory / f"{prefix}_candidate_fruit_mutations.vcf.gz"
        if hashlib.sha256(path.read_bytes()).hexdigest() != VCF_SHA[prefix]:
            raise ValueError(f"Source checksum mismatch at {path}")
        result[tree] = compare(path, by_key, {k[:4] for k in by_key}, tree)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    print(json.dumps(run(parser.parse_args().source), indent=2))
