# TMD recovery-transport research follow-up

Ricardo Maldonado · 1 October 2026 · Exploratory methods and prospective research

Start with [the formulation and next empirical test](FORMULATION_AND_NEXT_EMPIRICAL_TEST.md), then [the reproducible sensitivity analysis](transport_robustness/README.md) and [independent internal review](TRANSPORT_MATH_REVIEW.md).

The biological priority remains an authenticated, prespecified matched route/control panel. This follow-up reuses all 160 published synthetic outputs and adds a chosen-count recovery-confounding counterexample. It integrates earlier methods rather than claiming a new mutation mechanism or statistical principle. All 44 tests pass. Independent checks confirm 640 original projections, 800 sensitivity-grid evaluations and 40 exact compatibility-frontier certificates.

Reproduce from this directory with Python 3.12.14 (only the standard library is needed):

```sh
python3 -m unittest discover -s transport_robustness -p 'test_transport_robustness.py' -v
python3 transport_robustness/run_reanalysis.py --check
python3 verify_transport_review.py --public-archive ../TMD_research_extension_0_5_0_2026-09-30.zip
```

The independent oracle writes its deterministic review receipt beside itself. Copy this directory to a scratch location before regenerating receipts or result files if preserving an untouched checkout. `run_reanalysis.py --check` compares outputs without rewriting them.

[Environment reproduction evidence](ENVIRONMENT_REPRODUCIBILITY.md) distinguishes successful computational checks from the original release's strict floating-result identity failure. [Publication candidate](PUBLICATION_CANDIDATE.md) describes a proposed next methods version; it is not a publication receipt. The current released archive remains 0.5.0, expanded report 0.1.0, and historical software v2.6.5.

New code is MIT; new documentation is CC BY 4.0 under the repository licensing terms. Preserved public source artifacts retain attribution and their existing terms. Prepared with AI assistance; internal independent review is not external peer review.
