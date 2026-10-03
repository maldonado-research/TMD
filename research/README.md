# TMD recovery-transport research follow-up

Ricardo Maldonado · 1 October 2026 · Exploratory methods and prospective research

Start with [the formulation and next empirical test](FORMULATION_AND_NEXT_EMPIRICAL_TEST.md), then [the reproducible sensitivity analysis](transport_robustness/README.md) and [independent internal review](TRANSPORT_MATH_REVIEW.md). The [five-source literature update](literature/LITERATURE_UPDATE_2026-10-01.md) develops competing explanations; the [public source eligibility audit](public_dataset_audit/AUDIT_REPORT.md) verifies a published table inventory without relabeling its measurements as TMD trials.

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

## Public-source audit reproduction

The source XML remains outside this repository. To reproduce against the inspected local snapshot, supply its path explicitly:

```sh
python3 public_dataset_audit/reproduce_audit.py --source /path/to/sane_pmc.xml --output /tmp/tmd_public_source_audit.json
```

Alternatively, the script can attempt an official public acquisition with `--fetch-source`. Only the pinned source hash is accepted. The supplementary workbooks were not acquired, and no raw-workbook analysis or new biological test is reported.

## Continuing research rounds

The [continuation protocol](continuation/README.md) records the requested GPT-6.1 Sol Ultra setting, persistent checkpoints, an hourly workflow and a daily changed-source watch. The workflow is merged and explicitly paused. Its [single manual test](continuation/MANUAL_TEST_2026-10-02.json) skipped inference; the [checksum-verified artifact](continuation/ARTIFACT_READBACK_2026-10-02.json) now identifies the historical missing provider key and reproduces the collector's blocked receipt. Current Actions secret metadata remains inaccessible. The first new [drift-source audit](drift_audit/DRIFT_AUDIT_2026-10-01.md) reconciles biological and technical units and a model-conditional census residual; it supplies no matched W/A/M panel or establishment estimate. [Independent internal review](drift_audit/INDEPENDENT_REVIEW.md) checks the source identities, calculations and limits.

The second [matched-panel eligibility audit](panel_eligibility/README.md), dated 2 October 2026 UTC, authenticates four primary articles. Original notes, structured measurement ledgers and offline verification preserve source overlap, actual sampling units and unacquired-data limits. No complete matched panel is admitted. The [prospective design round](prospective_design/README.md) is now complete as design-only, with a frozen operational prediction algorithm and independently checked synthetic fixtures. Twenty-six study inputs remain unresolved; this is not a registered experiment. The changed-source watch and actual measurement contract are next.

## Latest source and numerical follow-up — 2 October 2026

The [bounded source watch](source_watch/2026-10-02/README.md) inspects three primary articles and two unchanged preprint records. A transcription-dependent hotspot in SBW25 provides a specific mutation-supply alternative, while population-history and plasmid-masking studies sharpen endpoint and observation limits. New in this watch means absent from the inspected public baseline notes, not a new scientific discovery or independent cohort. All three source identities/dates, 72 paragraph pins and 12 response hashes replay against the external cache; [independent source review](source_watch/INDEPENDENT_REVIEW_2026-10-02.json) checks the claims and licenses.

The [certified score candidate](certified_score/README.md) implements the R3 expected-log-score target using exact rational CP brackets, bounded logarithm series and box/simplex projection. The same simultaneous region covers all frozen comparators. It preserves full endpoint ledgers, strict gates, explicit resource caps and conditional-law requirements; zero qualifying counts remain unevaluable. The illustrative result is inconclusive. Its pre-outcome 0.05-nat half-width calculation needs 527/921 qualifying endpoints, beyond the 500-unit prototype cap. This supplies no power, biological effect, causal mechanism or registered study, and none of the 26 actual study inputs is filled.

Current [publication status](PUBLICATION_STATUS.md) supersedes the earlier draft checkpoint: record23113326 is now published with inherited0.5.0 files and no version label. The reviewed0.6.0 ZIP remains absent, and no active draft is verified. Ownership/authentication works; historical metadata/binary staging failed. Coordinate future writes with the publishing task and preserve the existing DOI family.
