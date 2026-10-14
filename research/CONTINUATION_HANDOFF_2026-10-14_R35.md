# TMD continuation checkpoint: R35, 14 October 2026

The [sample-provenance audit](calibration_sample_provenance/REPORT.md) follows R34's successful processed-source calibration replay with a different question: which actual released run, experiment, library and sample annotations underlie its 22 rows, and can the missing condition be named? The target and literal join rules were declared before inspecting the new experiment records. No additional calibration regression, author code or FASTQ pipeline is run.

## Authoritative identifiers and named candidate omissions

New official BioProject, eSearch, SRA experiment-package XML and BioSample records identify 178 project experiment packages and eight registered BioSamples. Every retained Figure 2D SRR joins exactly once to a distinct SRX and explicitly named library. All 22 target records refer to SRS22380613 / BioSample SAMN43151561 (soil_rDNAmimics). All literal primer and nominal mass labels agree with Figure 2D. This authenticates an archive-identifier crosswalk, without proving actual extraction ancestry, one physical specimen, shared laboratory pooling or independent biological units. The library suffixes are identifiers without an authenticated replicate role.

Exactly 24 released records match the specified soil mass/mix-E library-name pattern. The two extras are:

| Candidate run | Experiment | Literal library name |
| --- | --- | --- |
| SRR30280226 | SRX25741059 | V4_soil300mgmixE_S16 |
| SRR30280227 | SRX25741058 | V4_soil300mgmixE_S15 |

These are named V4/300-mg candidate omissions from the selected Figure 2D table. The source article reports a fewer-than-ten-standard-read exclusion for that condition, but neither an accession-specific assignment nor the processed counts for these candidates is recovered. SRA run read totals are different quantities. Released candidate records do not establish all attempted extractions, PCRs or sequencing failures, and 24 is not admitted as the attempted-sample denominator.

## Archive metadata and remaining uncertainty

A separate reviewer authenticates the 171 previously acquired regular members and screens the 94 substantive table/workbook/Rmarkdown/HTML members for metadata. No candidate run/experiment/library identifiers, processed counts or explicit exclusion assignments are found there. These are bounded record checks, not another figure analysis or an exhaustive review of nontext figure content.

Six lowest-mass SRRs are labeled 37.5 in Figure S3 and 37 in Figure 2D/2E/S4/S5 and in the corresponding library names. Literal source labels are preserved; actual weighed mass and its uncertainty remain unknown. The already reviewed R34 calculation retains its declared 37-mg predictor. No new fit, CI, power, source performance or biological sample-size calculation follows from the discrepancy.

The BioSample attributes have not-applicable collection date, geographic location, isolation source and isolate, and missing latitude/longitude. They do not supply dose or extraction/library ancestry. SRA Pool/Member metadata repeats the submitted sample annotation; it is not a physical laboratory pool ledger. The article's general equimolar second-round amplicon pooling statement and Figure 1's technical-replicate labels do not define Figure 2D's biological units. Approximate source-level DNA-copy dosing after bead-beating lysis remains distinct from actual row-level introduced-dose uncertainty, pre-entry cell recovery or mutation birth.

A fresh filename delta of the previously named local archive subtree finds zero added/removed paths among 11224 names and unchanged bytes/hashes for twelve prior named files. Private paths, fingerprints and document payloads remain outside Git. This bounded filename/identity comparison is not an exhaustive body search or proof of global absence; it admits no new biological record.

## Reproduction, review and accounting

The original public parser and verification commands are in the [report](calibration_sample_provenance/REPORT.md). Root separately parses the original XML/table; a separate Astra delegate implements independent archive/member and identifier checks without reusing producer derivation code. These are internal source/computational reviews, not qualified external biological assessment. Original response bodies, raw source tables and author code remain outside Git. Original synthesized joins and decisions retain source attribution and distinguish source/NCBI terms from licenses on our own work.

There are five conservatively counted scientific acquisition attempts and four successful responses. One default-sandbox request fails before HTTP and acquires zero body bytes; the authorized retry uses inherited proxy/TLS and explicit network permission. New saved source bytes total 1536860: 1500664 original structured-response bytes, 29275 Firecrawl-wrapper bytes and 6921 HTTP/failure-receipt bytes. Reused R33/R34 sources and derived outputs are not counted again; wire/provider-internal bytes are unknown. No new project/author Zenodo request, biological experiment or outreach occurs.

All 276 prior checkpoint fingerprints and all 44 study/planning NULLs remain preserved. Actual native stock/events, matched Wsp/Aws/Mws panel, biological count law, calibration/input uncertainty and biological TMD validation remain unresolved. No new theorem or native fit is established. Frozen algorithms, theta/eta, comparators, error allocation, stopping and paused automation are unchanged. Managed runtime165 is current/running with enforced networking; no credential value is read.

Reviewed GitHub/site publication remains authorized. Methods 0.6.0, DOI10.5281/zenodo.23219776, remains the frozen snapshot and excludes later R1–R35 addenda; no new project Zenodo version is created.

**Next priority, R36:** Obtain the processed per-standard counts, QC thresholds and accession-specific exclusion assignments for SRR30280226 and SRR30280227, or an actual extraction/PCR/library genealogy and row-level spike-dose/dilution uncertainty ledger linking the retained source runs. The 24 released condition-label records are not the complete attempted-sample denominator; one registered BioSample and distinct SRX/library names do not establish physical samples or independent biological trials. Preserve the literal 37 versus Figure S3 37.5 nominal labels and the R34 declared replay; do not silently change inputs or refit. An actual native MPB10583/MPB10613 stock/pedigree/sequence crosswalk or authoritative Figure 9 replicate/correction/aggregation record remains an alternative priority. Use the 44-field qualified-review worksheet before native admission, with origin/ancestry, inherited negatives, exposure, establishment, named-stage recovery and invisible-loss records, complete separately frozen predictors/comparators and evaluation, and propagated identified uncertainty. Park repeated unchanged SRA/BioSample or missing-record lookups, another figure replay and unsupported mathematical extensions. Preserve all 26 study and 18 planning NULLs, R5/R11/R17, theta/eta, error allocation, stopping, paused runner and methods 0.6.0. No outreach or laboratory work.
