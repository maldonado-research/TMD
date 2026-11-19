"""Reproduce aggregate candidate and fruit-tissue counts in Schmitt et al.'s v2 data."""
import argparse
import csv
import gzip
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

DATA = "https://doi.org/10.5281/zenodo.10089692"
PAPER = "https://doi.org/10.1073/pnas.2313312121"
CODE = "https://github.com/sylvainschmitt/treemutation/blob/fc6a2eeef7b2bb1d178ebfbf3a79652ca13fb9df"
BASE = "treemutation_save/02_mutations"
MEMBERS = {
    "D_leaves": ("02_filtered/angela.leaf_mutations_spectra.tsv.gz",
                 "cd340e3989ce17c45343fc50a058c2704acb8e766f60e7554b2ec7aa51e22fad"),
    "S_leaves": ("02_filtered/sixto.leaf_mutations_spectra.tsv.gz",
                 "46b6c60e4896cd85b7c291335fa876b47649b58c05050266c33ff2ac556d2de2"),
    "D_list": ("02_filtered/angela.fruits_candidate_mutations.tsv.gz",
               "45d99d58633e2ae51cdbbe93af8b77ddf81f907f7285612f131021e68d5be39a"),
    "fruit": ("04_fruits/fruit_mutations.tsv.gz",
              "ac860196c362ee608dddffb5883a3cab9db2c5c9a4869dc90be1caca96c7d328"),
}
SPECIES = {"Dicorynia guianensis": "D", "Sextonia rubra": "S"}


def source_tables(zip_path, directory):
    if zip_path is not None:
        with ZipFile(zip_path) as archive:
            payloads = {k: archive.read(f"{BASE}/{name}") for k, (name, _) in MEMBERS.items()}
    else:
        payloads = {k: (directory / Path(name).name).read_bytes() for k, (name, _) in MEMBERS.items()}
    tables, sources = {}, {}
    for key, data in payloads.items():
        name, digest = MEMBERS[key]
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"Changed source member: {name}")
        sources[key] = {"member": f"{BASE}/{name}", "gzip_bytes": len(data), "sha256": digest}
        tables[key] = list(csv.DictReader(io.StringIO(gzip.decompress(data).decode()), delimiter="\t"))
    return tables, sources


def leaf_key(row):
    return (int(row["CHROM"].removeprefix("Super-Scaffold_")), int(row["POS"]), row["REF"], row["ALT"])


def fruit_key(row):
    return int(row["scaffold"]), int(row["position"]), row["normal"], row["mutation"]


def candidate_set(rows, tree):
    # The cited notebooks apply the published evs filter and count qualifying observations.
    sample_rows = set()
    by_key = Counter()
    for row in rows:
        branch = row["branch"]
        eligible = branch in ("A", "B", "C", "D") if tree == "D" else branch[:1] in ("F", "C", "B", "E")
        if row["Filter"] == "evs" and eligible:
            key = leaf_key(row)
            observation = (key, row["tumor"])
            if observation in sample_rows:
                raise ValueError("Duplicated candidate/leaf observation")
            sample_rows.add(observation)
            by_key[key] += 1
    return {key for key, observations in by_key.items() if observations >= 3}


def fruit_counts(rows, candidates):
    tissues = sorted({r["tissue"] for r in rows})
    positive = defaultdict(set)
    observed = set()
    for row in rows:
        key = fruit_key(row)
        observed.add(key)
        if row["heterozygous_call_gatk"] not in ("0", "1"):
            raise ValueError("Unrecognized published call flag")
        if row["heterozygous_call_gatk"] == "1" and float(row["allelic_fraction"]) > 0:
            positive[row["tissue"]].add(key)
    if not observed <= candidates:
        raise ValueError("Filtered fruit-table record outside reconstructed candidate frame")
    any_positive = set().union(*positive.values())
    embryo_label = positive["embryo sac"]
    cotyledon = positive.get("cotyledon", set())
    remaining = any_positive - embryo_label - cotyledon
    return {
        "reconstructed_candidate_keys": len(candidates),
        "fruit_table_rows": len(rows),
        "distinct_keys_in_filtered_fruit_table": len(observed),
        "distinct_keys_with_positive_in_any_listed_tissue": len(any_positive),
        "distinct_positive_keys_by_literal_tissue_label": {t: len(positive[t]) for t in tissues},
        "distinct_positive_keys_in_embryo_sac_or_cotyledon": len(embryo_label | cotyledon),
        "keys_only_positive_outside_embryo_sac_and_cotyledon": len(remaining),
        "outside_only_keys_with_positive_by_tissue": {
            t: len(remaining & positive[t]) for t in tissues if remaining & positive[t]
        },
        "candidates_absent_from_filtered_fruit_table": len(candidates - observed),
    }


def analyze(zip_path, directory):
    tables, sources = source_tables(zip_path, directory)
    if set(r["species"] for r in tables["fruit"]) != set(SPECIES):
        raise ValueError("Unexpected trees")
    results = {}
    for species, tree in SPECIES.items():
        candidates = candidate_set(tables[tree + "_leaves"], tree)
        if tree == "D":
            saved = {leaf_key(r) for r in tables["D_list"]}
            if saved != candidates or len(tables["D_list"]) != len(saved):
                raise ValueError("Independent deposited Dicorynia candidate list differs")
        rows = [r for r in tables["fruit"] if r["species"] == species]
        results[species] = fruit_counts(rows, candidates)
    return {"article": PAPER, "dataset": DATA, "source_members": sources,
            "archived_code": [f"{CODE}/{name}" for name in
                              ["11-MutationsAngela.Rmd", "12-MutationsSixto.Rmd", "40-Figures.Rmd"]],
            "Dicorynia_deposited_candidate_list_equals_reconstructed": True,
            "species": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--zip", type=Path, help="Original treemutation_save.zip")
    group.add_argument("--members", type=Path, help="Directory with the four extracted compressed tables")
    args = parser.parse_args()
    print(json.dumps(analyze(args.zip, args.members), indent=2, ensure_ascii=False))
