"""Recover the isolate labels and aggregate molecular assignments in the R28 ledger."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

LEDGER_SHA256 = "f2215be3622462efc9ce008ead9d8cc02311aa2a35f866be5c63c75d2df3fed5"
SOURCE_COMMIT = "604390d9bba8471be26487e3737c072a0f5cb9bf"
SOURCE_PATH = "research/matched_source_feasibility/DERIVED_SOURCE_AUDIT.json"


def replay(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != LEDGER_SHA256:
        raise ValueError("Input differs from the pinned historical ledger")
    cohort = json.loads(data)["historical_cohort"]
    rows = cohort["rows"]
    labels = [r["isolate_label"] for r in rows]
    expected = {"WS" + chr(n) for n in range(ord("A"), ord("Z") + 1)}
    if len(labels) != len(expected) or set(labels) != expected:
        raise ValueError("Unexpected historical roster")
    counts = Counter(row["molecular_table_route"] for row in rows)
    counts["Unresolved"] = counts.pop(None)
    if counts != cohort["molecular_table_counts"]:
        raise ValueError("Molecular row assignments differ from the ledger summary")
    codes = {"Wsp": "W", "Aws": "A", "Mws": "M", "Unresolved": "WAMO"}
    return {
        "source_url": f"https://github.com/maldonado-research/TMD/blob/{SOURCE_COMMIT}/{SOURCE_PATH}",
        "source_sha256": LEDGER_SHA256,
        "distinct_isolates": len(labels),
        "allowed_classes": {codes[key]: value for key, value in counts.items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    print(json.dumps(replay(parser.parse_args().ledger), indent=2, sort_keys=True))
