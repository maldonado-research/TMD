"""Extract the four generation-zero pooled assays for each published yeast pair.

Requires Python 3.9+ and pyreadr. See FOUNDER_SOURCE.md for pinned inputs.
"""
import argparse
import csv
from hashlib import sha256
import math
from pathlib import Path

import pyreadr


FITNESS_SHA = "f20f592d570614b0add41d1181900570e75338f73bffdae95100e98001e03f3d"
EVOLUTION_SHA = "f10be28895efc07a2106f8de08e38661ccc75139826e919ffe54b170aa41d9e0"
CONDITIONS = (
    "CMdiploid0.001", "CMhaploid0.001", "CM+Ethanoldiploid0.001",
    "CM+Saltdiploid0.001", "CMdiploid0.004", "CMdiploid0.00025",
)
REPLICATES = range(1, 5)
COLUMNS = (
    "population_id", "condition_id", "assay_pool_id", "replicate",
    "initial_A", "final_A", "initial_B", "final_B", "initial_ref", "final_ref",
    "initial_pool_reads", "final_pool_reads", "fit0_A", "fit0_B",
)


def read_native(path, digest, object_name):
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"{path.name} differs from the pinned author table")
    return pyreadr.read_r(str(path))[object_name]


def order_label(source_set, label):
    # The previous W### extraction orders the base barcode IDs.
    last = {"S14": 6, "S2": 7}.get(source_set, 1)
    if label in {f"d1{letter}{i}B" for letter in ("A", "H") for i in range(2, last + 1)}:
        return label[:-1]
    return label


def positive_count(value):
    if not (value >= 1 and float(value).is_integer()):
        raise ValueError(f"Invalid pseudocount-inclusive measurement {value}")
    return int(value)


def harmonic_mean(values):
    return len(values) / sum(1 / value for value in values)


def fitness_rows(data):
    identifiers = ["treatment", "set", "bc1", "bc2", "ref"]
    fields = ["fit0"]
    fields += [f"{quantity}0r{rep}" for rep in REPLICATES for quantity in ("fit", "rfit")]
    fields += [f"{count}_{time}_0r{rep}" for rep in REPLICATES for time in ("i", "f")
               for count in ("bc1cts", "bc2cts", "refcts", "ppects")]
    baseline = data[identifiers + fields].drop_duplicates()
    if len(data) != 608 or len(baseline) != 152:
        raise ValueError("Expected four copies of the baseline measures per founder")
    grouped = data.groupby(["treatment", "bc1"], observed=True)
    if not (grouped.size().eq(4).all() and grouped["rep"].nunique().eq(4).all()):
        raise ValueError("The evolved-assay copies do not match the four source rows")
    lookup = {}
    for _, entry in baseline.iterrows():
        key = (entry["treatment"], entry["bc1"])
        if key in lookup:
            raise ValueError(f"Duplicate native founder key {key}")
        values = []
        weights = []
        for rep in REPLICATES:
            def counts(time):
                return [positive_count(entry[f"{kind}_{time}_0r{rep}"])
                        for kind in ("bc1cts", "refcts", "ppects")]

            ci, ri, ni = counts("i")
            cf, rf, nf = counts("f")
            fit = math.exp((math.log(cf / rf) - math.log(ci / ri)) / 20)
            weight = harmonic_mean([harmonic_mean([ci, ri, ni]), harmonic_mean([cf, rf, nf])])
            if not (math.isclose(fit, entry[f"fit0r{rep}"], rel_tol=1e-13)
                    and math.isclose(weight, entry[f"rfit0r{rep}"], rel_tol=1e-13)):
                raise ValueError(f"Native ancestral fitness or weight disagrees for {key}")
            values.append(fit)
            weights.append(weight)
        summary = sum(f * w for f, w in zip(values, weights)) / sum(weights)
        # R apply() coerced this mixed-type data frame to a character matrix.
        # For these pinned columns its decimal formatting rounded the fitnesses
        # to seven decimal places and the weights to four.
        formatted_weights = [round(weight, 4) for weight in weights]
        formatted_summary = (sum(round(value, 7) * weight
                                 for value, weight in zip(values, formatted_weights))
                             / sum(formatted_weights))
        if not (math.isclose(summary, entry["fit0"], rel_tol=0, abs_tol=4e-8)
                and math.isclose(formatted_summary, entry["fit0"], rel_tol=1e-14)):
            raise ValueError(f"Native weighted summary disagrees for {key}")
        lookup[key] = entry
    return lookup


def extract(fitness_path, evolution_path, output):
    lookup = fitness_rows(read_native(fitness_path, FITNESS_SHA, "myfa"))
    metadata = read_native(evolution_path, EVOLUTION_SHA, "myevo")[
        ["wid", "treatment", "set", "bc1", "bc2"]]
    if len(metadata) != 76 or metadata["wid"].nunique() != 76:
        raise ValueError("Unexpected longitudinal well design")
    pools = sorted({entry["set"] for entry in lookup.values()})
    pool_ids = {pool: f"F{i:03d}" for i, pool in enumerate(pools, 1)}
    used = set()
    rows = []
    for i, (_, well) in enumerate(metadata.iterrows(), 1):
        labels = sorted((well["bc1"], well["bc2"]),
                        key=lambda name: order_label(well["set"], name))
        keys = [(well["treatment"], name) for name in labels]
        a, b = (lookup[key] for key in keys)
        if (a["bc2"] != labels[1] or b["bc2"] != labels[0]
                or a["set"] != b["set"] or a["ref"] != b["ref"]):
            raise ValueError(f"Founder pairing disagrees at well {i}")
        used.update(keys)
        for rep in REPLICATES:
            def count(entry, kind, time):
                return positive_count(entry[f"{kind}_{time}_0r{rep}"])

            for time in ("i", "f"):
                for kind in ("refcts", "ppects"):
                    if count(a, kind, time) != count(b, kind, time):
                        raise ValueError(f"Unshared reference or pool depth at well {i}")
                if (count(a, "bc1cts", time) != count(b, "bc2cts", time)
                        or count(a, "bc2cts", time) != count(b, "bc1cts", time)):
                    raise ValueError(f"Mismatched reciprocal count at well {i}")
            rows.append((f"W{i:03d}", CONDITIONS.index(well["treatment"]) + 1,
                         pool_ids[a["set"]], rep,
                         count(a, "bc1cts", "i"), count(a, "bc1cts", "f"),
                         count(b, "bc1cts", "i"), count(b, "bc1cts", "f"),
                         count(a, "refcts", "i"), count(a, "refcts", "f"),
                         count(a, "ppects", "i"), count(a, "ppects", "f"),
                         repr(float(a["fit0"])), repr(float(b["fit0"]))))
    if len(used) != 152 or len(pools) != 12 or len(rows) != 304:
        raise ValueError("Incomplete founder or pool coverage")
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fitness", type=Path, help="Author myfa.Rdata")
    parser.add_argument("evolution", type=Path, help="Author myevo.Rdata")
    parser.add_argument("output", type=Path, help="Destination TSV")
    args = parser.parse_args()
    extract(args.fitness, args.evolution, args.output)
