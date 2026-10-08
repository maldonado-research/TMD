"""Reproduce finite synthetic event-capture design identities externally."""
import argparse
import json
from pathlib import Path
from event_capture import benchmarks


def main():
    if not __debug__:
        raise SystemExit("Verification requires ordinary Python without -O/-OO.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-against", type=Path)
    args = parser.parse_args()
    encoded = (json.dumps(benchmarks(), indent=2)+"\n").encode()
    if args.check_against and encoded != args.check_against.read_bytes():
        raise SystemExit("Stored event-capture benchmark differs")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    result = json.loads(encoded)
    print(json.dumps({"status": result["status"], "checks": result["checks"],
                      "biological_fit": False}))


if __name__ == "__main__":
    main()
