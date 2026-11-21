# Separate-assay forecasts across endpoint libraries

The ten-repeat proof-of-concept assay identified **15–18 of 21** day-25 leaders across the four possible assignments of original or rerun libraries to the two endpoint pools. The day-0 leader identified **11–12**, and adding the day-0 ratio to the assay identified **13–16**. The predicted direction of change in share was correct in **10–11** wells. The combined forecast reduced mean absolute share error by 0.00133 to 0.01645 across the four assignments.

| S11 (10 wells) | S14 (11 wells) | Day-0 leader hits | Assay leader hits | Combined leader hits | Gain-direction hits | Endpoint leaders changed from archived |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Original | Original | 12 | 15 | 13 | 10 | 5 |
| Original | Rerun | 11 | 16 | 14 | 10 | 2 |
| Rerun | Original | 12 | 17 | 15 | 11 | 3 |
| Rerun | Rerun (archived choice for both) | 11 | 18 | 16 | 11 | 0 |

This exploratory sensitivity check holds the starting measurement, founder profiles and projections fixed. Every well in a pool receives the same endpoint-library choice. Both libraries provide positive depth for all 21 wells. The two libraries measure the same evolved samples. [Source study](https://doi.org/10.7717/peerj.10118) · [Endpoint pool data in TMD 0.11.0](https://doi.org/10.5281/zenodo.24382132)

Run `python -B check_proof_endpoints.py` from this directory. The JSON output records all four assignments, hit counts and absolute share errors. The script uses the Python standard library and checks the four input files against their SHA-256 digests.
