# Reproduction in the cloud environment

Checks performed 1 October 2026 (America/Los_Angeles), using Python 3.12.14 and NumPy 2.3.5. Only standard-library Python is needed for inference and the new transport follow-up; NumPy is used by the prior calibration generator.

## Verified capabilities

- Expanded-report suite: 16 tests passed.
- Methods 0.5.0 suite: 13 tests passed.
- Full 0.5.0 calibration rerun: all 160 synthetic datasets retained; rejection counts 0/40, 0/40, 40/40 and 0/40. Independent seed/count/exact-projection replay passed. Low-recovery results remain unbounded-compatible.
- README timing CLI: synthetic deviance approximately 148.158854, permutation p=0.0005.
- rpoB secondary calculation: source metadata and counts reproduced exactly, including 111 isolates and held-out score gain 13.125728780024541 bits.
- Public-source eligibility audit: the authenticated main-article table inventory reproduced byte-identically; an independent reviewer checked table order, all count vectors, aggregates and dependence caveats. Supporting workbooks were not acquired.
- New robustness follow-up: 44 tests, all 160 original public decisions, 640 projections, 800 sensitivity evaluations, 40 exact frontier certificates, six boundary fixtures and 48 independently checked chosen-example CP endpoints passed.

Generated analyses ran outside the original tracked release files. The released ZIPs, source scripts and archived expected outputs were preserved.

## Failed strict identity checks and diagnosis

The original `audit/verify_exact_binomial_coverage.py` fails its complete-JSON equality assertion for `high_recovery_strong_departure.json` in this environment. Five other fixtures reproduce exactly. In the affected fixture, floating root proposals alter ten related fields; the selected Aws upper endpoint differs by about 1.13e-12 and the lower endpoint by two floating ULPs. This original audit remains **failed** and is not counted as a passed check.

Independent direct integer-binomial summation certified all 171 current and all 171 archived nonboundary endpoints. All six fixture decisions agree. A diagnostic changing two `math.lgamma` outputs by one ULP reproduced the archived fixture fields exactly, isolating floating-proposal portability. This does not justify modifying expected outputs or disabling certificates. The original oracle reaches its fixture loop only after checking its small-count rational PMFs, tails, coverage grid and projection corners; its later checks do not complete in the failed invocation.

The rpoB strict JSON comparison also differs in one floating field by 5.55e-17. Counts, metadata and the substantive result agree; floating summaries agree within 2e-14. This is not byte-identical reproduction.

The new follow-up avoids regenerating these floating proposal endpoints: it preserves and hashes the exact public 0.5.0 ZIP member containing all 160 archived confidence results, reconstructs their rational projections and makes transport/intersection/frontier decisions using rational arithmetic. Its preserved calibration source SHA256 is `509783c2a67bf70e590b3daca4b7f9706cf4c9a6b578a5e4e318e47939dd819f`.

## Interpretation

Successful tests demonstrate the documented computational capabilities and selected synthetic behavior. They do not authenticate biological sampling, control transfer, a mechanism, universal power or novelty. The strict archived-output portability issue remains a documented limitation of the prior release.
