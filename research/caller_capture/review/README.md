# Independent exact caller review

The fixed 5,693,331-byte oracle was frozen before producer inspection. Offline SciPy/HiGHS proposed attaining laws and dual coefficients; exact Fraction equalities and inequalities certified both endpoints. The generator is not included and is not a standard-library implementation. The included certificate verifier needs only Python's standard library and can verify the fixed oracle without SciPy or producer imports. Every case is synthetic.

From the parent directory:

```sh
python3 -B review/verify_blind_r22_certificates.py --oracle review/R22_BLIND_ORACLE.json --output /tmp/tmd_r22_certificates.json
python3 -B review/compare_r22.py --engine caller_capture.py --oracle review/R22_BLIND_ORACLE.json --selection review/R22_ALL_FROZEN_CASES_SELECTION.json --output /tmp/tmd_r22_comparison.json --marginal-n-cap 4
```

The stdlib replay checks 207,327 certificate/full-law identities. All 66 full-law cases and 2,889 frozen marginal grid cases agree with the producer, using 55,108 comparisons, witness and normal guard checks. The earlier 603-case subset is included and is not counted twice. Thirty-seven admission guards also pass under each of -O/-OO; these optimized checks are separately counted. Producer benchmark replay has 185 checks. These are internal mathematical/API checks, not empirical confidence coverage, native-caller authentication, clinical findings or qualified external review.
