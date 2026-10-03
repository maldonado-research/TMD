# Public empirical source eligibility audit

Audit date: 1 October 2026 (America/Los_Angeles; 2 October UTC).

**Outcome: the primary article and its Table 1 were authenticated and inventoried; the supplemental workbooks were not acquired.** The counts below are reproduced from the article, not newly verified workbook rows or new biological measurements. This descriptive audit performs no TMD hypothesis test and reports no new mathematical result.

## Source and acquisition status

Sane, Parveen and Agashe (2025), *Mutation bias alters the distribution of fitness effects of mutations*, PLOS Biology, published 14 July 2025. DOI: [10.1371/journal.pbio.3003282](https://doi.org/10.1371/journal.pbio.3003282); [PMC12273949](https://pmc.ncbi.nlm.nih.gov/articles/PMC12273949/).

The public PMC XML was already obtained by the parallel literature review through [NCBI EFetch](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=12273949). This audit reused those bytes and verified the main article's DOI, PMC accession, Table 1, supporting-information identities, and CC BY 4.0 license statement. Reviewer correspondence is excluded from the extraction. The 220,656-byte source snapshot has SHA-256 `a6477b003ba58cb2ab7249f96459e14a409fc6ed7c37ce450f9e2c8cfebdb0ea`. A hash identifies this fetched snapshot; it is not independent verification of the experiments.

The main article identifies:

| Source | Author-described contents | Source filename | Audit status |
| --- | --- | --- | --- |
| S2 Data | Number and type of mutations present in each mutation-accumulation (MA) line | `pbio.3003282.s023.xlsx` | Bytes not received; sheets, columns and rows unverified |
| S3 Data | Raw fitness for single-mutation MA lines, measured in LB and glucose | `pbio.3003282.s024.xlsx` | Bytes not received; sheets, columns and rows unverified |

The PMC article and an `articles/instance/12273949/bin/` S3 link returned HTTP 200 with a reCAPTCHA HTML page, not an XLSX archive. Those responses were rejected as data. The NCBI Open Access API returned HTTP 404 at both tested official host/path variants. The [publisher S2 endpoint](https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3003282.s023&type=supplementary) failed with a proxy CONNECT 403 even after `journals.plos.org` was added to the proposed environment allowlist; the draft did not make that endpoint reachable in this session. The corresponding [S3 endpoint](https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3003282.s024&type=supplementary) remains a candidate for a later permitted acquisition, not an authenticated download. No CAPTCHA or network restriction was bypassed. Exact attempts are recorded in `ACQUISITION_STATUS.json`.

The article states that relevant data are in the paper and supporting information and carries CC BY 4.0. Separate workbook notices, metadata and any additional terms could not be inspected. The audited article describes laboratory *E. coli* observations, with no human-subject records identified in the material inspected. No third-party raw XML, workbooks or PDFs belong in the public artifact bundle. The original report, extraction script, derived table aggregates and hashes can be reviewed independently; local source bytes remain under ignored `raw/`.

## Reproduced article-table inventory

These are author-reported counts from main-article Table 1. The exclusion column is arithmetic subtraction of successfully sequenced lines from evolved lines. It is a sequencing-stage accounting quantity, not an independent Bernoulli recovery assay or a per-route detection probability.

| Strain/background | MA lines evolved | Successfully sequenced | Sequencing exclusions by subtraction | Single-step fitness comparisons |
| --- | ---: | ---: | ---: | ---: |
| ΔmutS | 350 | 345 | 5 | 91 |
| ΔmutL | 350 | 344 | 6 | 97 |
| ΔmutH | 350 | 346 | 4 | 100 |
| Δnth-nei | 300 | 285 | 15 | 102 |
| WT | 98 | 97 | 1 | 94 |
| ΔmutY | 430 | 424 | 6 | 113 |
| ΔmutT | 300 | 271 | 29 | 97 |
| **Total** | **2,178** | **2,112** | **66** | **694** |

The source table also sums to 4,642 mutations in the sequenced lines. This mutation count uses the broader sequenced-line collection; it must not be assigned to the 694 fitness comparisons as if they were the same sampling unit. No beneficial/deleterious counts, success rates, confidence intervals or raw-fitness summaries were calculated here.

## Units, grouping and missingness

**The 694 comparisons are not 694 independent founding-line trials.** Table 1 footnote c specifies that 80 of the 94 WT observations came from the first block, which contained only 38 founding MA lines. Forty-six of those observations represent second-, third- or fourth-step mutations. Their fitness effects were measured against the immediate ancestor carrying earlier mutations. The remaining 14 WT observations came from the second block. A row identifier alone therefore cannot establish lineage independence or a common ancestral baseline.

Methods report fitness measurements of the same isolates in LB broth and M9 minimal salts plus 5 mM glucose. These media are paired conditions, not separate independent collections. Each fitness estimate uses the mean of three technical replicates. The article describes maximum exponential growth rate relative to the relevant ancestor, with selection coefficient derived from relative growth rate. This is a laboratory growth proxy, not a direct establishment probability, fixation outcome or first successful-arrival time.

MA experiments used differing durations and multiple blocks. High-mutation-rate backgrounds could have a separate ancestor per block. The construction process also produced background mutations in the mutators except Δnth-nei, according to Methods. WT and ΔmutY include observations described in prior work; a future combined literature dataset must prevent duplicate reuse. These design features matter for aggregation, adjustment and train/test partitions.

Mutation calls required strand support, at least four reads per strand, and frequency greater than 80%; the authors investigated additional low-frequency variants in sensitivity analyses. A "single mutation" here is qualified by that calling procedure and, for later WT steps, by an immediate-ancestor comparison. The authors also corrected their DFEs for selection during colony growth. Uncorrected growth values and bias-corrected DFE frequencies are different quantities.

Methods report excluded WGS samples with insufficient or absent reads, consistent with the table-level difference of 66. Individual exclusions, blank fitness cells, failed growth assays, plate identities, formula caches, replicate exports, clone identifiers and lineage joins remain **unverified** because the workbooks were unavailable. In particular, multiplying 694 by two media or three technical replicates does not verify that many complete exported records. The source inventory cannot establish a missing-at-random assumption.

## Relevance and eligibility limits

This published experimental panel provides a concrete reason to include mutation spectrum, repair background, ancestral background and environment-specific performance among competing explanations for observed evolutionary patterns. The present contribution is a source and eligibility audit of that panel. It does not reproduce the paper's DFE inference or test a competing TMD model.

It is ineligible for the current Wsp/Aws/Mws contrast: those competing routes, common-background winner counts, independently estimated matched route supply, and route-specific recovery-control trial denominators are not provided by the audited inventory. The seven repair backgrounds cannot be relabeled as the three TMD routes. The two media cannot supply two eligible route-frequency contexts merely because both contain fitness measurements. MA endpoint fitness measurements also cannot be fitted as first-arrival survival observations. Sequencing completion counts cannot substitute for introduced/recovered fixed-route controls.

For the next acquisition protocol, require persistent founding-culture, lineage, mutation-step, immediate-ancestor, block, plate and replicate identifiers; preserve the pairing between media; record exact ascertainment and failed-assay stages; distinguish technical replicates from biological trials; and identify prior-publication reuse. Build held-out sets at a justified biological cluster level rather than splitting paired records or steps of the same lineage across training and test sets. Obtain genuinely matched supply, selected outcomes and recovery controls before applying the existing route model. None of those controls can be reconstructed by assuming uninspected fields contain the needed records.

## Reproduction and remaining work

The standard-library script reads the pinned PMC XML, checks article identity and supplement labels, extracts the four relevant Table 1 rows, checks the WT lineage qualification, and emits `derived_aggregate.json`. It intentionally produces no workbook summaries. From this directory:

```sh
python reproduce_audit.py --source raw/sane_pmc.xml
```

A fresh public acquisition can be attempted with `python reproduce_audit.py --fetch-source`; a changed XML hash stops processing and requires source review. This guards against silently treating a revised or different source as the audited snapshot. The JSON marks raw workbook availability and TMD eligibility explicitly. Reproduction was run twice with byte-identical output; the source checks and the 694-count sum passed. The aggregate and original public-safe files are listed in `SHA256SUMS.txt`.

The finite remaining acquisition step is to obtain S2/S3 through an accessible official endpoint, verify ZIP/Open XML structure and the authoritative response provenance, hash the bytes, then inspect actual sheets, fields, units, lineage/ancestor joins, and missingness. Until that happens, this is an **article-derived inventory and eligibility audit**, not a completed raw-data reanalysis.

Original audit and extraction software: Ricardo Maldonado, prepared with AI assistance; documentation and derived summaries CC BY 4.0, new code MIT under the repository licensing terms. Source researchers retain attribution and their original rights. An independent internal reviewer checked the table vectors and aggregate against the authenticated XML; this is not external peer review.
