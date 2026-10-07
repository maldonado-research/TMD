#!/usr/bin/env python3
"""Replay conditional synthetic fluctuation benchmarks without source fitting."""
import argparse
import json
from pathlib import Path
from conditional_fluctuation import benchmarks

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--check-against", type=Path)
    a = p.parse_args()
    result = benchmarks()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.check_against:
        assert text == a.check_against.read_text(), "synthetic replay differs"
    a.output.write_text(text)
    print(json.dumps({k: result[k] for k in ["status", "exact_finite_clone_thinning_identities",
                       "exact_compound_Poisson_relative_coefficient_identities",
                       "infinite_clone_rational_tail_checks", "biological_likelihood_fits"]}))

if __name__ == "__main__":
    main()
