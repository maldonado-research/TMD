# TMD 0.5.0 inference lineage

Copyright (c) 2026 Ricardo Maldonado. All code in this directory is released under the accompanying MIT LICENSE.

This implementation is a new standard-library confidence-projection kernel, rather than a modification of the 0.4.0 Newton solver. The fixed-route count topology and scientific contract descend from TMD 0.4.0. The explicit marginal-law declarations and acceptance of observed zero/all-success counts are new. The 0.4.0 artifacts remain unchanged. Known Clopper–Pearson tail inversion, Bonferroni simultaneous coverage, and monotone rectangular projection are used; no external mathematical novelty or validated biological mechanism is claimed.

Runtime: Python 3.10 or later, standard library only. No SciPy, NumPy or other third-party dependencies. `boundary_confidence.py` provides `simultaneous_confidence(document, alpha='0.05')`, plus `clopper_pearson(k, n, tail_error)` and `project_context(intervals)`. Run the CLI from the extracted package root:

```
python3 inference/boundary_confidence.py inference/fixtures/high_recovery_strong_departure.json --alpha 0.05
python3 -m unittest discover -s inference -p 'test_*.py' -v
python3 inference/run_synthetic_validation.py
```

`make_synthetic_fixtures.py` regenerates the deterministic input tables. These tables have no biological provenance. The separate repeated-sample calibration is a synthetic computational study, not a theorem of power.
