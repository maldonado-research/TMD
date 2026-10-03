# A census-measurement audit of the public genetic-drift release

Research date: **1 October 2026, America/Los_Angeles**; source retrieval occurred 2 October UTC.

This finite research round inspected small official public files from Ascensao, Yu and Hallatschek, *The evolution of genetic drift over 50,000 generations* ([journal DOI](https://doi.org/10.1093/genetics/iyag199)). It produced a new descriptive audit of replication, colony-count coverage and technical count discrepancies. It did not refit genetic drift, test TMD on biological W/A/M outcomes, or independently replicate the paper's evolutionary result.

## Provenance and exact scope

The source is the public [genetic-drift-evolution repository](https://github.com/joaoascensao/genetic-drift-evolution), release `Genetics`, commit `c1b47a977a9307281917ac1dee29861a813a7fd2`, tree `f7df5cc44e2a648a9e9215e55d46620ce4daa7fc`. At inspection, `main` was `7c19b447b67e14e451552d0c8bba1825e299d09a`, a later commit with message `Update README.md`. The audit uses the release, not a moving branch.

Read-only `gh api` calls obtained repository/commit/tag metadata, complete tree listings, and an explicit allowlist of 19 small files: release README, master experiment ledger, five batches' experiment lists/sample metadata/CFU files, and two inference scripts read for measurement definitions. All decoded inputs match both their pinned Git blob SHA-1 and recorded SHA-256. The API responses total **2,091,916 bytes**, below the **20,000,000-byte** limit. No raw FASTQ, barcode trajectories, posterior samples, private material or 1.49-GB archive was downloaded; no upstream code was executed. The CFU summary files contain original colony counts, unlike posterior draws.

The earlier literature round's primary preprint XML and Zenodo metadata were reused as local evidence, with SHA-256 recorded separately. Detailed protocol statements refer to **PMC12873942.1, January 27, 2026 preprint version 1**; the journal Methods were not inspected. The [Zenodo version record](https://doi.org/10.5281/zenodo.21431098) identifies version `Genetics`, links its GitHub tag, and declares CC BY 4.0. Its archive has not been downloaded or hash-compared to the GitHub blobs. GitHub's license field is null, and its complete inspected tree contains no license file. Accordingly, archive metadata establishes a declared archive license, without establishing a blanket redistribution claim for every GitHub input. Raw third-party evidence is ignored and excluded from the public-file allowlist.

## Actual replication and coverage

The master ledger and five batch lists reconcile exactly:

| Recorded unit | Count | Meaning |
|---|---:|---|
| LTEE evolutionary populations | 2 | Ara+2 and Ara−2; longitudinal samples share ancestry |
| Clone names | 33 | 16 from each evolved population plus REL606 ancestor |
| Culture timecourses | 67 | 32 evolved clones with two replicates each; ancestor with three |
| Sequencing metadata rows, assay days 0–4 | 335 | Sample/index mappings, not independent mutant trials or verified read outcomes |
| Additional preassay sequencing metadata row | 1 | REL606 replicate 1, day −1 |
| CFU timepoint rows | 268 | Four distinct days per recorded culture, days 0–3 |
| Recorded plate counts | 474 | 268 first counts and 206 second counts |
| Missing second counts | 62 | Missing measurements, preserved as missing |
| Blank formatting rows excluded | 4 | E5 CSV rows with all fields empty |

The preprint's “BarSeq experiments” paragraph `P40` specifies day-separated replicates using the same strain barcode library, generally two timecourses and three for REL606. “Measuring genetic drift parameters” describes clone monocultures. Thus 67 culture timecourses do not supply 67 independent evolutionary histories. Barcode libraries, barcodes, reads, daily samples, clones and evolutionary populations occupy different levels of the design. Ara−2 ecotypes share population history; Ara+2 A/B clone labels do not themselves establish separate phylogenetic branches.

## A model-conditional technical census residual index

Preprint `P40` describes repeated nominally identical dilution/plating procedures, including **100 microliters plated**, for two technical measurements. “Bayesian inference of genetic drift parameters,” `P67–P68`, states that colonies were counted and uses a common dilution factor for both replicates; some second measurements are missing, for example after contamination. The pinned inference scripts pass `CFU1` and `CFU2` directly as integer counts, with dilution supplied separately, and give both counts the same `Nb * D` mean. They are not CFU density estimates multiplied by an unknown scale.

For rows with both counts (X,Y) and positive total, this audit computes

\[
Q=\frac{(X-Y)^2}{X+Y}.
\]

Under an ideal **independent, equal-exposure Poisson** reference, conditioning on (S=X+Y>0) gives (X\mid S\sim\mathrm{Binomial}(S,1/2)), hence (E[Q\mid S]=1). The protocol and author likelihood justify that nominal reference; individual realized dilution and plated-volume exposures were not independently verified from per-plate laboratory records. The statistic therefore remains model conditional. Equal nominal exposure does not guarantee identical pipetting or colony formation.

Across the **206 paired rows**, mean (Q) is **4.937810**, median (Q) **1.832851**, and the median absolute pair difference relative to the pair mean is **13.20%**. Sixty-nine rows have (Q>4); this is a descriptive threshold count, with no significance claim. There are no observed zero-count plates. The index describes count disagreement against the specified reference; it is neither the author's fitted CFU overdispersion parameter nor genetic drift. Handling, dilution/plating variability, unequal realized exposures or contamination can contribute. Shared culture-density variation that moves both plates together is not measured by their difference.

| Batch | Culture timecourses | CFU rows | Paired rows | Missing second plate | Mean Q |
|---|---:|---:|---:|---:|---:|
| E1 | 1 | 4 | 0 | 4 | — |
| E23 | 19 | 76 | 68 | 8 | 6.479850 |
| E4 | 16 | 64 | 60 | 4 | 5.412802 |
| E5 | 15 | 60 | 40 | 20 | 2.720532 |
| E6 | 16 | 64 | 38 | 26 | 3.762360 |

Missingness also clusters by day: **all 15 E5 day-0 rows** and **all 16 E6 day-2 rows** lack the second count. Its cause is not identified by these files. Batch/population summaries therefore describe the available pairs; they do not identify biological differences between populations. No across-row independence, missing-at-random assumption, p-value or confidence interval is claimed. The practical result is that a count-only Poisson reference is an inadequate descriptive account of available technical discrepancies and that batch/day coverage must remain visible when using census data to separate abundance from drift. This is consistent with the authors' explicit census-noise model, rather than independent validation of their posterior estimates.

## Observation and inference boundaries

Barcode reads and counted colonies are observed. True barcode cell frequencies, bottleneck size, descendant-number variance, effective size and measurement-error terms are inferred through a joint model. The preprint's “Bayesian inference of genetic drift parameters,” `P59–P70`, separates sequencing error from latent frequency dynamics and CFU noise from abundance. The two inspected release scripts make these distinctions explicit. Posterior draws do not add biological replication, and marginal summaries of abundance and descendant variance do not retain their joint posterior dependence.

The inferred descendant variance concerns a **dilution-to-dilution cycle**, rather than a single generation. Neutral clone-monoculture variance does not directly measure establishment of a particular adaptive mutant in another ecological context. Per-cycle versus per-generation selection, arrival phase within a growth cycle, mutant genotype and competition all affect that transfer. The preprint discusses more than one absolute establishment approximation; this audit imports no absolute establishment probability and does not resolve those approximations against the journal version or supplementary derivation.

No route-specific mutation-production assay, observed beneficial-mutant establishment count, matched Wsp/Aws/Mws selected-outcome ledger, exact introduced-single-cell recovery denominator or validated recovery-control transfer was found in the inspected scope. **Zero matched W/A/M ledgers are admitted.** Counts, barcode trajectories and censuses must not be repurposed as such trials. Reusing this paper's summaries would also not produce a new independent study.

## What would distinguish mutation supply from drift prospectively

1. Measure **route-specific mutation supply per division** independently in the same background and context, including repair state and relevant sequence targets. Record divisions and time. Supply uncertainty belongs in the comparison rather than being absorbed into an unexplained route adjustment.
2. Obtain independent **condition-matched neutral trajectories plus census and technical-noise calibration**, retaining culture/day/batch structure. These can separate abundance from reproductive variance under their observation model. They cannot substitute for the preceding mutation-supply measurement.
3. Measure **growth and low-copy establishment of defined route mutants** in the relevant background and ecological setting. Preserve per-cycle effect units and arrival phase. Record exact introduction/recovery denominators and assess control transfer separately from establishment. A neutral-background variance cannot automatically be assigned to every adaptive mutant.
4. Before selected held-out outcomes are examined, freeze supply-only, supply-plus-independent-establishment, restrictive TMD and flexible context/background predictions. Reserve whole contexts or later culture blocks; preserve all competing routes, censoring and detection lags. Two shared historical populations cannot identify a general causal drift effect.

If route enrichment disappears under measured route-specific supply, that supports the supply explanation for that comparison. If matched supply is stable but mutant survival changes as predicted by independently measured reproductive variance, that supports an establishment-side explanation under the tested conditions. A drift factor common to all routes can change the overall successful-arrival clock while canceling from normalized W/A/M winner shares; a changed route contrast requires route/background differences, which must be measured. The present public summaries cannot decide those alternatives.

## Reproduction and public scope

From this directory, run `python3 fetch_public_inputs.py` to fetch the explicit small-file allowlist or reuse cached inputs, then `python3 audit_summaries.py`. `--refresh` makes read-only API calls again and enforces the same per-audit cumulative response budget; it does not download the release archive. The reproduced outputs are `derived/summary.json`, batch, batch/day and population CSV aggregates. Previously retrieved protocol/license evidence is recorded separately; the fetch script does not retrieve the journal full text. On a fresh copy, restore the two locally excluded protocol/license snapshots from the source URLs listed in `INPUT_MANIFEST.json` and verify their recorded SHA-256 hashes before running. The fetch script validates and preserves existing evidence records; it stops if a recorded snapshot is missing or changed.

Only original notes, scripts, manifests, status, review receipts and derived aggregates appear in `PUBLIC_FILES.json`. Third-party raw files remain under ignored `raw/`, and public-safe status means preparation for review, not external publication. This audit made no edits under `/workspace/TMD`; concurrent parent-task changes are outside this round.

Original analysis prepared for Ricardo Maldonado's TMD research with AI assistance. Upstream study, data and methods remain attributed to Joao A. Ascensao, QinQin Yu and Oskar Hallatschek. New code uses MIT and new documentation CC BY 4.0 under the TMD project's licensing terms; source materials retain their own rights.
