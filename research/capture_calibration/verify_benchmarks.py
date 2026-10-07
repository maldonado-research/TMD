"""Reproduce exact conditional capture-calibration benchmarks externally."""
import argparse
import json
from pathlib import Path
from capture_calibration import benchmarks


def main():
    if not __debug__:
        raise SystemExit("Verification requires ordinary Python without -O/-OO.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-against", type=Path)
    args = parser.parse_args()
    output = (json.dumps(benchmarks(), indent=2) + "\n").encode()
    if args.check_against and args.check_against.read_bytes() != output:
        raise SystemExit("Stored capture-calibration benchmark differs")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    print(json.dumps({"status": "passed", "checks": json.loads(output)["checks"],
                      "biological_fit": False}))


if __name__ == "__main__":
    main()
