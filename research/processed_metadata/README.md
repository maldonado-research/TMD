# PTATO processed-data admission update

Mutation by Natural Dominance · R000024 · 8 October 2026, America/Los_Angeles

The official [Mendeley version 1 record](https://data.mendeley.com/datasets/c3r9chw9rb/1) and two exact metadata files are now authenticated. This advances the R23 artifact assessment to **METADATA_AUTHENTICATED_NO_NUMERICAL_BENCHMARK_ADMITTED**. It supplies sample relationships and exposes two reproducible metadata checks. No variant-level recovery calculation, native origin benchmark, biological TMD fit or qualified external scientific review is obtained.

## Authenticity and access

The version-1 record for DOI **10.17632/c3r9chw9rb.1** names the PTATO paper and gives publication time 30 May 2023. Its own license metadata specifies **CC BY 4.0**, including attribution, license-link and change-indication requirements and a caveat for third-party content. This is dataset-specific evidence, separate from the article license. It does not establish authorization for the controlled EGA accession EGAS00001007288 or remove participant privacy obligations.

The official root-file endpoint lists four files: Table_S1.txt (10,174 bytes), Table_S2.txt (1,780), Table_S3.txt (1,514) and SV_Counts_FA.txt (1,543), with SHA-256 hashes and file identifiers. This is a **root-level inventory**, not a recursive release manifest. The roughly 1.03 GB complete archive was not downloaded. The two acquired tables have byte counts and SHA-256 hashes exactly equal to this inventory. The unmodified UTF-8 bytes of Firecrawl's raw-content fields match; no newline repair or reconstruction was needed. Exact source hashes and observed official URLs are in [PROVENANCE.json](PROVENANCE.json).

Six bounded acquisition calls by the data-access agent returned 1,078,560 bytes when their complete tool responses were serialized as documented. That number includes duplicated MCP text/structured envelopes and is not a measurement of HTTP wire traffic. One metadata request returned JSON error 400 despite HTTP 200; a folder request returned HTTP 404. Neither is represented as a manifest. A separate root-agent call acquired Table S1 and is excluded from the six-call subtotal. The connector's internal HTTP request count is not exposed. No unchanged PMC CAPTCHA endpoint was retried.

## Sample structure and training

Table S2 has **16 records and 12 columns**: one bulk, six clone, five subclone and four PTA rows. Three PTA rows are marked Training=No; the FANCC PTA row and its preceding subclone are marked Training=Yes. The recovery loop selects every PTA row without a Training filter (Figure2.R line 1374), so its four-group frame includes this flagged training branch. These author-recorded flags support an explicit training/evaluation inventory; they do not independently certify untouched evaluation or per-variant labels.

The source code chooses each PTA row's preceding assayed clone/subclone by the common Clone field and the greatest other Days_after_clone value (Figure2.R, lines 1378–1383). On the authenticated table this gives one predecessor for each PTA row, and every resulting day difference equals that row's Days_after_sort. The WT comparisons cover 87 and 84 days; the FANCC comparison is day 58 to day 114 (56 days); the MSH2 comparison is day 84 to day 131 (47 days). These are culture-duration metadata, not observed divisions or independently measured ancestry. The four rows do not establish four independent founder histories. Batch identifiers, all attempted/failed cultures and lost-lineage genotypes remain unavailable.

Table S1 has **79 records and 16 columns**: 26 PTA, 40 clone and 13 bulk rows. Twelve rows are marked Training=Yes (nine PTA and three bulk), and 67 are marked No. Its source column assigns 41 rows to this study, 16 to Brandsma 2021 and 22 to Osorio 2018. Those are row counts, not independent biological sample counts or three independent experiments. All four individual labels represented in Training=Yes rows also occur in Training=No rows. Consequently, a No flag on a sample row alone cannot establish donor-level holdout. This overlap does not identify the exact training variants or demonstrate leakage. The public audit publishes only aggregate counts, without individual identifiers or clinical attributes.

## Reproducible label discrepancy

The two WT recovery-bar identifiers are reversed between Table S2 and the archived figure code. Table S2's C19SC1 row is labelled WT-PTA1 and its C6SC1 row WT-PTA2; Figure2.R lines 1462–1463 assign C6SC1 to WT-PTA1 and C19SC1 to WT-PTA2. Both conventions are retained in [METADATA_AUDIT.json](METADATA_AUDIT.json), which records the source row numbers and code lines. This is a demonstrated identifier-annotation mismatch. It does not by itself establish a wrong aggregate result, and the displayed figure output was not recomputed.

## What remains before numerical admission

The authenticated metadata closes the narrow question of whether genuine Table S2 input is available and strengthens the artifact-specific license and sample-mapping evidence. **No whole admission gate is fully satisfied** by this acquisition. The nine-gate update is recorded in [ADMISSION_UPDATE.json](ADMISSION_UPDATE.json).

The concrete next acquisition is a bounded recursive manifest for the three relevant AHH-1 cell-line directories, followed by eligible paired PTA and SMuRF variant files, filtered-header cutoff metadata, callability BEDs and comparison-caller records. A narrowly named genotype-stage replay must retain the preceding-clone CLONAL/PASS_QC and VAF conditions, chr17 exclusion, per-sample denominators, missing/QC outcomes, sample-averaged summaries and cross-sample variant-name membership in CallableVariants. Table-level CallableLoci fractions cannot substitute for the required locus records. The WT label map and training flags must travel with every reported sample result.

Neither table supplies independent acquisition-episode truth, inherited/pre-existing origin-negative variants, all-birth inclusion or lost-lineage limits. Caller uniqueness, absence or missing states do not establish a new origin. The native matched system, transport argument and qualified biological/statistical assessment remain unchosen or outstanding. All 26 actual study inputs and 18 control-planning fields remain unresolved. The model, route requirements, complete frozen forecasts, eta, context weights, exclusions, simultaneous error allocations and stopping rule are unchanged.

## Replay and reuse

Run `python3 -B verify_cached_sources.py --cache /path/to/sources --figure-code /path/to/Figures/Figure2.R`. The checker reads local cached sources, verifies their pinned bytes, replays the aggregate/mapping audit and prints a receipt. A missing cache cannot be replaced by package hashes. Third-party responses, both raw metadata tables, external code and any biological inputs remain outside Git and outside the public package.

Prepared by Ricardo Maldonado with AI assistance. Original documentation and summaries are CC BY 4.0; original checker code is MIT. Source artifacts retain their own terms. Internal source verification is not qualified external scientific review.
