# What the SBW25 hotspot figure data actually measure

Ricardo Maldonado · TMD research round R000006 · 7 October 2026, America/Los_Angeles

The licensed public figure-data archive behind Farr and colleagues' SBW25 hotspot study is now acquired and checksum verified. Original code reproduces the supplied reporter-frequency calculation for all **24 culture occurrences**, time-course arithmetic, competition coefficients from supplied ratios, and the selected transcript-proxy calculation. These are measurements in an established mutation-supply alternative. **They provide no complete Wsp/Aws/Mws panel, native mutation-rate calibration, or biological confirmation of TMD.** All 26 actual study inputs remain unresolved.

Article: Farr, Vasileiou, Lind and Rainey (2025), *An extreme mutational hotspot in nlpD depends on transcriptional induction of rpoS*, [10.1371/journal.pgen.1011572](https://doi.org/10.1371/journal.pgen.1011572). Dataset: Andrew D. Farr, [10.5281/zenodo.14335473](https://doi.org/10.5281/zenodo.14335473), deposited 9 December 2024, CC BY 4.0. The dataset record is a source of this audit and belongs to its own publication family; it is not a TMD release.

## Acquisition and experimental units

Two unauthenticated public HTTPS requests returned **7,885,276 bytes**, within the 20 MiB and 12-source round limits. The ZIP has 7,880,751 bytes, advertised and verified MD5 `c07253f941ce89ceb594187255ba085a`, and SHA-256 `9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6`. All 82 entries were inspected for traversal, symlinks and encryption; expanded size is 15,018,225 bytes. There are **28 research files**, 38 excluded operating-system metadata files, and 16 directories. Raw reads, workbooks, machine paths, resource forks, and article text stay outside the public candidate.

Figure 4A comprises six individual reporter transformants per background, each used on two occasions: **12 culture occurrences per background, 24 overall**. The primary caption calls these 12 biological replicates; the methods specify transformant reuse. Preserve both descriptions without asserting perfect independence of repeated transformants or separately authenticated construction events. Nested colony confirmations, selective plates, sequencing reads and individual cells are different sampling units. Eleven FASTQ/FASTQ.GZ files contain **711 read records**, not 711 independent biological trials.

## Reproduced reporter endpoint frequency

Let `H` be counted size-qualified selective colonies, `I` the number of selective plates, `J` the culture dilution fraction, `L/M` the confirmed C565T fraction among sequenced colonies, and `E` the terminal nonselective plate CFU count. The workbook implies 50 µL per plate and a terminal nonselective dilution of 10⁻⁶. `J` alone is not the fraction of the whole 6 mL culture sampled; that would also require the number and volume of plates:

\[
\widehat C_{\mathrm{candidate}}=\frac{H}{I(0.05)J},\qquad
\widehat C_{565}=\widehat C_{\mathrm{candidate}}\frac LM,\qquad
\widehat N=20\,10^6 E,
\]

\[
\widehat f=\frac{\widehat C_{565}}{\widehat N}
=\frac{HL}{IJME\,10^6}.
\]

The script preserves the source integer candidate counts, plate counts, dilutions and confirmation denominators in a derived ledger. It uses exact fractions for this calculation, then compares cached workbook values at a fixed relative tolerance of 2×10⁻¹² and absolute tolerance of 10⁻³⁰. Cached floating serialization residuals are recorded; exact byte or exact decimal equality is not claimed. All 144 underlying formula texts, including shared OOXML formulas, match their stated dependencies.

| Occasion | Background | Culture occurrences | Confirmed / sequenced | Mean corrected terminal frequency |
|---|---|---:|---:|---:|
| 1 | SBW25 reporter | 6 | 34 / 48 | 3.03878×10⁻⁶ |
| 1 | SBW25 ΔpsrA reporter | 6 | 47 / 47 | 2.73591×10⁻⁸ |
| 2 | SBW25 reporter | 6 | 26 / 48 | 5.98842×10⁻⁶ |
| 2 | SBW25 ΔpsrA reporter | 6 | 48 / 48 | 4.85173×10⁻⁸ |

Ratios of those **mean terminal frequencies** are 111.07 and 123.43 for the two occasions; the pooled descriptive ratio is 118.97. The article's MSS mutation-rate point estimates instead imply **58.33**. Frequency includes clone expansion, survival, plating, size selection and confirmation. Corrected fractional CFU estimates are not directly observed mutational births. The difference between these two contrasts does not contradict the article; they estimate different quantities. **The FALCOR/MSS fit, its input conversion, model settings and confidence intervals were not reproduced.** No new inferential test, sampling confidence interval or causal mutation-rate estimate is reported.

## Unresolved source gaps

Figure 4A occasion 1 SBW25 replicate 5 records **7 counted candidate colonies but 8 sequenced colonies**. This prevents treating the recorded candidate count as a verified closed finite sampling pool. The source's confirmation correction is replayed as written, while the sampling-frame mismatch remains open.

The occasion 1 workbook totals **95 sequenced colonies**, but its FASTQ contains **94 reads**. The unavailable SBW25 read is `MPB38311` colony 8. The ΔpsrA group `MPB38420` has 7 reads and a workbook denominator of 7, so its missing eighth nominal colony is already reflected in the workbook. Absence from the acquired FASTQ is a provenance gap, not proof that a reported colony never existed.

A restricted diagnostic maps the reference's annotated codon 189 to reporter position 2023, corresponding to article nlpD base 565. It requires unique exact 15-base outer anchors around a three-base window and target Phred+33 quality at least 20. All 96 occasion 2 reads meet the rule and their per-transformant T counts match the workbook. Occasion 1 has 88 callable reads and 6 unresolved reads. No alignment rescue or genotype imputation is used, and diagnostic counts do not overwrite the article's counts. Native Figure 1 files contain 142 reads for the unmodified nlpD cohort, and 76 paired-direction reads for 38 Q189W isolates. A read count alone does not reconcile the article's 139 selected cell-chaining outcomes or establish first-event denominators.

The S4 time course has 24 destructively sampled culture occurrences over two occasions, with two cultures at each of six times per occasion. Its 213 recorded sequencing confirmations include **24 follow-up colonies** after an initially negative confirmation sample, for a 32-colony denominator at one time/replicate. Outcome-dependent confirmation sampling is retained. The second occasion FASTQ filename/README says 96, while actual content has 95 initial reads; with 24 follow-ups, available counts agree with the final workbook total of 119 for that occasion. The earliest second-occasion sample also excludes one contaminated plate, using seven plates and 0.35 mL rather than eight plates and 0.4 mL. No time-dependent mutation-rate fit is attempted.

## Transcript and fitness proxies

Figure 4B's selected plotting values are **log₂ transcript proxies**. The script matches all 12 values to 22-hour genotype/replicate entries and checks the average of two technical Ct runs. It also authenticates the selected well labels: rows B/F assay nlpD 5′ and C/G assay nlpD 3′. Thus `ΔCt = Ct3′ − Ct5′` and the supplied proxy is `2^(-ΔCt) = 2^(Ct5′−Ct3′)`. Mean log₂ proxies are 3.48520 for SBW25 and 0.909809 for ΔpsrA. Their difference yields a **5.9603 geometric-mean linear-proxy ratio**; the ratio of arithmetic means after exponentiation is 6.1488. These use the supplied ideal doubling transform, without new efficiency calibration or fluorescence processing. A ratio of log₂ means, 3.8307, is **not** a linear fold change.

The article's main text describes approximately a sixfold transcription reduction, while its Figure 4B caption says approximately fourfold. Both source statements are retained. Their difference is not silently resolved or attributed to a particular author calculation. Transcript abundance is an assay proxy, not a calibrated native mutation-supply parameter.

The S2 reporter-fitness workbook provides 32 competition occurrences with marker swaps across two occasions. The script checks the supplied per-generation selection coefficient, `ln(final mutant/WT ratio ÷ initial ratio) / log₂(final population ÷ initial population)`, and retains marker/occasion strata. The group means vary by marker and occasion, including small negative values. Raw cytometry gates and absolute fitness were not re-estimated, and no significance claim is added. Exact neutrality of reporter mutants should not be assumed.

## Consequence for the next TMD test

The study experimentally connects transcriptional regulation to an engineered reporter hotspot. The regulator deletion is an intervention in that reporter system. It does not identify transcription as the sole mediator, because regulator genotype can also affect other cellular processes. The results support mutation supply as a concrete competing mechanism for evolutionary parallelism. They do not calibrate the native hotspot from the reporter, identify a separate dominance force, or replace inheritance, selection, establishment, recovery and drift.

The next useful contract must specify the native/reporter genotype and locus, culture/transformant/occasion hierarchy, timing and growth history, actual selective colony pool, sequencing missingness, plating fractions, assay model and fitness effects **before** selected outcomes are used to choose a forecast. [The measurement-gap ledger](MEASUREMENT_CONTRACT_GAPS.json) separates acquired measurements from unresolved transport prerequisites. No model parameter or study-registry field is filled from these selected endpoint data.

## Reproduction and scope

Python 3.12 and the standard library suffice; no R, spreadsheet application, aligner or FALCOR service is executed. Acquire the public ZIP separately with [the bounded downloader](fetch_sbw25_data.py), or supply the already acquired pinned file:

```sh
python3 fetch_sbw25_data.py --output-directory /tmp/tmd_sbw25_source
python3 reproduce_sbw25_audit.py \
  --zip /tmp/tmd_sbw25_source/source_data.zip \
  --output /tmp/tmd_sbw25_replay.json \
  --check-against DERIVED_MEASUREMENT_AUDIT.json
```

The full deterministic replay passes **504 Figure 4A numeric/plot checks, 144 formula-text checks, 144 time-course checks, 96 competition-calculation checks and 98 transcript arithmetic/mapping checks**. Assertions authenticate and reconcile this particular source; their count is not a count of independent observations or hypotheses tested. [The verification receipt](VERIFICATION_RECEIPT.json) records outputs and scope. [Independent internal source and methods review](review/REVIEW_NOTES.md) checks the corrected primer labels, exact frequencies, experimental units and scope; its [receipt](review/REVIEW_RECEIPT.json) pins the reviewed candidate. Two legacy XLS workbooks and other qPCR sheets were inventoried but not quantitatively reprocessed. Source versions beyond the pinned dataset record, original AB1 traces and unavailable laboratory records were not acquired. This is an exploratory public-source audit with AI assistance, not external peer review or a registered experiment.

Original code is MIT; original notes and derived numerical summaries are CC BY 4.0 under the repository's terms. Underlying dataset attribution and CC BY 4.0 apply to its numerical measurements. See [license and privacy review](LICENSE_AND_PRIVACY_REVIEW.json). Raw files and third-party article text are excluded from this public candidate.
