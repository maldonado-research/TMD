# Native mutation-origin controls: evidence before interpretation

Mutation by Natural Dominance · R000021 · 7 October 2026, America/Los_Angeles

This source-grounded evidence plan strengthens the review packet for a future cancer-relevant measurement pilot. It does not obtain qualified external review, choose a laboratory or establish an actual native origin-inclusion control. Every actual planning value remains unfilled; all 26 existing bacterial study fields remain unresolved.

Three different targets must stay separate: callable genomic territory, correctness/sensitivity of a variant classifier in its declared reference frame, and inclusion of a distinct mutation-origin event after ancestry, survival and the native caller. Neither high coverage nor high conditional classifier sensitivity supplies the third quantity.

## What the selected evidence adds

- PTA 2021, DOI [10.1073/pnas.2024176118](https://doi.org/10.1073/pnas.2024176118), compares single-cell genotypes with bulk reference and kindred cells. Its germline benchmarks, five-day expansion and live-cell frame do not enumerate lost origins. The reported 99.9% germline precision coexists with a mean 2,785 false-positive genome-wide calls: the target and denominator matter.
- PTATO 2023, DOI [10.1016/j.xgen.2023.100389](https://doi.org/10.1016/j.xgen.2023.100389), provides artifact-filtering and clonal-validation leads. Reported 86.8% conditional classifier sensitivity differs from 45–69% recovery of shared substitutions. Its ENU reassessment reuses the earlier PTA dataset; some accuracy estimates use signature refitting because exact artifact truth is unknown. Sample-adaptive thresholds, reference absence and recurrence exclusions need native validation.
- NNK 2026, DOI [10.1021/acs.chemrestox.6c00154](https://doi.org/10.1021/acs.chemrestox.6c00154), supplies a recent animal mutagenicity benchmark with positive controls and two readouts. Six rats were dosed but five per group assayed; the two methods use the same DNA. Their reported r=.99 is concordance, not a second independent biological replication or a known-origin sensitivity experiment.

These are leads and limits from published observations. The three studies are not one common-background TMD panel. Repair, exposure, growth/loss, technical artifacts and ordinary selection remain competing explanations. No numerical sensitivity, response threshold, Poisson/binomial law or parameter is transferred into TMD.

## Reviewable deliverables

[CONTROL_EVIDENCE_LEDGER.json](CONTROL_EVIDENCE_LEDGER.json) contains 20 original source-specific measurement/transfer rows. [SOURCE_REVIEW.json](SOURCE_REVIEW.json) records 14 screened abstracts, exact source hashes and one-based paragraph anchors. Root read both 56-paragraph PTA/NNK main bodies; PTATO assessment is restricted to 25 listed paragraphs plus a short lead scan. Supplementary data, raw reads, third-party code and regulatory documents were not acquired. Public files contain original summaries and hashes, not article bodies or participant records.

[CONTROL_TRANSFER_PLAN.md](CONTROL_TRANSFER_PLAN.md) defines distinct evidence levels and failure conditions. [EXPERT_DECISION_PACKET.md](EXPERT_DECISION_PACKET.md) asks for qualified adjudication. [PROSPECTIVE_CONTROL_FIELDS.json](PROSPECTIVE_CONTROL_FIELDS.json) deliberately leaves all 18 actual planning choices null. None of these is a laboratory protocol, signed scope, registered experiment or medical intervention.

The [caller-aware methods](../caller_capture/README.md) illustrate how support/reference requirements alter event inclusion under explicit synthetic assumptions. They do not reconstruct the actual callers in these articles. A lower inclusion bound of zero cannot support a positive-inclusion correction by assertion; a positive bound still requires validated origin truth, observation and transport assumptions.

## Reproduction

Run the cached-source checker with explicit external outputs; it never fetches missing sources or writes to this package:

```sh
python -B verify_cached_sources.py --cache-dir /workspace/tmd-research-progress/r21_r22_review_2026-10-07/raw --output /tmp/tmd_r21_source_check.json
sha256sum -c SHA256SUMS.txt
```

The source XML cache is retained outside Git. Missing or mismatched cache produces an explicit UNRUN/failed result, not a claimed passing source replay. Hash checks establish identity rather than scientific correctness; the source interpretation needs separate review. No biological TMD fit, new theorem, priority or cancer-prevention result is established. Original code MIT; original notes/summaries CC BY4.0; source articles retain their own licenses and are not redistributed. Prepared by Ricardo Maldonado with AI assistance.
