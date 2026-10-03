# Recovery transport robustness of stored TMD confidence results

This standalone analysis combines the recovery mismatch sensitivity already described in TMD extension 0.3.0 with the exact interval decisions stored by extension 0.5.0. It reuses all 160 existing synthetic confidence results. It adds no biological observations, random datasets, mechanism validation, or mathematical novelty claim.

The question is how much independently bounded disagreement between actual recovery and recovery controls would make an apparent across-context departure compatible with a shared biological contrast.

## Results

`R` bounds each **differential residual across the two branches** by `[1/R,R]`. It does not separately bound each branch's recovery error. Residual vectors may differ across contexts.

| Preserved synthetic scenario | Records | Reject at R=1 | R=1.1 | R=1.25 | R=1.5 | R=2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reused 0.4 high-recovery stress | 40 | 0 | 0 | 0 | 0 | 0 |
| High-recovery shared contrast | 40 | 0 | 0 | 0 | 0 | 0 |
| High-recovery strong departure | 40 | 40 | 40 | 40 | 0 | 0 |
| Low-recovery shared-contrast stress | 40 | 0 | 0 | 0 | 0 | 0 |

The 80 high-recovery null records remain compatible with a finite interval. The 40 low-recovery records remain `compatible_unbounded`: their shared finite log contrast is not bounded on at least one side. Compatibility does not establish equality.

For the 40 initially rejecting records, the smallest common residual bound restoring interval compatibility ranges approximately from **1.262828358596 to 1.420489220553**. Every individual frontier has an outward exact rational bracket of width at most `2^-80`; decisions use rational eighth powers, not these rounded displays. These are sensitivity frontiers of a conservative confidence projection, not estimates of actual recovery mismatch or biological effects.

A separate illustrative fixed-route counterexample has the same biological `J=1` in two contexts but control-corrected observable `J=16` and `J=1/16`. For its chosen count tables, assuming exact transport rejects. The valid differential residual bound `R=2` restores a finite common interval containing 1. This is an arithmetic example, not a new Monte Carlo replicate or experimental result.

## Reproduce

Python 3.10+ and the standard library suffice. Run from this directory:

```sh
python -m unittest discover -s . -p 'test_transport_robustness.py' -v
python run_reanalysis.py --check
python validate.py
python transport_robustness.py example_bounded_mismatch_input.json --output /tmp/tmd_transport_example.json
```

`run_reanalysis.py` without `--check` regenerates the two deterministic result JSON files from the preserved source. It checks 640 context projections and all 160 original decisions before evaluating the sensitivity grid. No bootstrap, simulation, or old raw-count validator runs. `make_counterexample.py` regenerates only the illustrative chosen-count CP fixture; floating root proposals can vary across platforms, so the stored exact interval fixture is the replay reference.

## Files and scope

- `transport_robustness.py`: exact rational interval correction, explicit assumption contract, decisions, and certified threshold brackets.
- `run_reanalysis.py`: replay of all 160 stored synthetic records, five specified sensitivity scenarios, and the mismatch counterexample.
- `results/reanalysis.json`: every preserved record, exact adjusted interval, decision, and frontier certificate.
- `results/mismatch_counterexample.json`: the illustrative recovery-confounding example and both conditional analyses.
- `METHODS.md`: observation model, proof, assumptions, and limits.
- `IN_MORE_BASIC_TERMS.md`: interpretation without the algebra.
- `sources/MANIFEST.json`: hashes and paths of the preserved public 0.3.0 and 0.5.0 materials.
- `VALIDATION.json`: validation receipt; `SHA256SUMS.txt`: package file hashes.

The wrapper treats the 0.5 result as a confidence projection for an **observable control-corrected probability contrast**. The old raw-count validator requires exact biological recovery transport; this wrapper does not call it, modify its source, or adopt that assertion. Biological interpretation instead requires the explicit bounded-mismatch assumptions in the new input contract.

Each grid value is a hypothetical sensitivity bound. Nominal confidence statements require the actual differential residual to lie in bounds fixed independently of the outcomes. A frontier chosen after seeing the result is descriptive; it does not establish such bounds. Valid trial units, route probabilities, matched designs, and positive population components remain necessary. Raw declarations, hashes, and agreement with a reference file do not authenticate these scientific assumptions.

Source code and documents preserved in `sources/` retain their original attribution and license. The root `LICENSE` follows the existing public project's MIT license.
