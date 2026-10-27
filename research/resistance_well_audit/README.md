# Gifford resistance data: a bounded source audit

Ricardo Maldonado · 27 October 2026 · Original factual assessment with AI assistance

**The acquired files support a structural and descriptive audit of detected resistance. They do not supply a matched TMD panel or independently observed mutation origins.** No biological model was fitted, no source-author program was executed, and no publication error is established.

The source is Gifford et al. (2023), *Mutators can drive the evolution of multi-resistance to antibiotics*, [PLOS Genetics, DOI 10.1371/journal.pgen.1010791](https://doi.org/10.1371/journal.pgen.1010791). Its data statement links the [author repository](https://github.com/dannagifford/multi-resistance). This audit pins repository commit [`907311849f5610f114ed3ef99f5de73e51349b67`](https://github.com/dannagifford/multi-resistance/tree/907311849f5610f114ed3ef99f5de73e51349b67), dated 12 September 2022. The README references a preprint; the article link authenticates the repository relationship, but does not establish that this exact snapshot generated the 2023 publication.

## Acquired evidence and method

The bounded download obtained the three `1ul_individual_*.csv` files, three `1ul_aggregate_*.csv` files, `2018-06-08_ODvsNT.csv`, `README.md`, and `munging.R`. Every downloaded file matched its pinned Git blob identity; SHA-256 hashes are retained in `data_receipt.json`. The repository metadata and complete returned tree were also retained. The primary [NCBI XML](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=10292718&retmode=xml) identifies PMC10292718.1 and the article DOI: 206,517 bytes, SHA-256 `2e6b6bde457b78faed2c4f1db71818af9e33ba91522f95dff5b8e597ca600ccb`.

An original Python standard-library script verifies source hashes, reads CSV records strictly, checks composite assay keys, and expands recorded well lists. Static inspection of `munging.R` supplies the declared 60-label universe, B–K crossed with 2–7: `ALL` means that full set, `0` means an empty set, and a leading minus denotes its complement. No undocumented token repair is performed.

Comparisons use treatment, transfer volume, day, nominal mixture label and assay medium. The source program associates nominal labels 0/10/25/50 with ordered measured-frequency headers in each aggregate file. The audit follows that explicit recipe; it does not independently authenticate the underlying culture assignment. The numerical frequency headers differ between experiments and must not be replaced by nominal percentages. The aggregate counts are per-medium positive-well counts, not mutually exclusive resistance-state totals.

## Verified file-level findings

There are 384 assay records: four treatment labels × four mixture labels × six days × four assay media. The declared layout represents 960 logical longitudinal well slots and 5,760 possible well-day vectors. These arithmetic denominators do not authenticate independent founders, mutation events or the disposition of the five initially resistant cultures excluded according to article Methods, section `sec012`.

Two records in `1ul_individual_single.csv`, physical lines 175 and 183 including the header, contain eight fields under seven column names. They affect the day-six nalidixic-acid assay for the rifampicin/high-mixture and nalidixic-acid/low-mixture strata. Both entire assay records remain unknown. This leaves 382 syntactically admissible assay records, no duplicate composite keys, 5,640 complete four-assay well-day vectors and 840 complete endpoint vectors across 14 of 16 strata.

Among 381 syntactically admissible, nonmissing individual-versus-aggregate count comparisons, 54 disagree: 33 without drug, eight with rifampicin, seven with nalidixic acid and six with the combination. One aggregate value is `NA`; the two malformed records are not compared. These are disagreements between acquired representations under the source mapping. Their cause and the authoritative representation remain unresolved; this is not a reproduction or correction of the authors' published analysis.

All four combination-treatment endpoint strata have parseable records. The raw combination-medium detections and all-four-assays-negative observations are:

| Nominal mixture label | Combination-medium positives / declared wells | All four assays negative |
|---|---:|---:|
| 0 | 0 / 60 | 60 |
| 10 | 14 / 60 | 43 |
| 25 | 17 / 60 | 40 |
| 50 | 37 / 60 | 6 |

The aggregate file gives 40 rather than 37 in the last positive-count cell. Both representations are retained. All-negative observations are not automatically extinction, surviving sensitivity or absence of mutations. The source program groups all-negative and sensitive patterns into a simplified “no resistance” category; the audit preserves raw four-assay patterns separately.

## Biological and reuse limits

Article sections `sec014`–`sec019` distinguish repeated transfers, detection from a 1/200 population sample, growth measurements from independently derived clones, previously estimated mutation rates, selected sequenced isolates and subsequent fluctuation assays. These are different experimental units. They do not establish direct mutation births, route-specific division exposure, unseen losses or introduced/recovered fixed-route trial denominators. Earlier mutation-rate estimates are transported across environments under stated assumptions; they are not newly measured in every selection context.

The OD/CFU calibration table contains 36 records: six blanks, 30 samples and 27 numerical NT cells. Colony-count values repeat across dilution rows. Its well labels lack a shared biological identifier linking them to selection populations. Neither shared well labels nor matching dimensions justify such a join.

The article declares CC BY 4.0. Repository metadata reports no detected license, and no license file was found in the inspected tree; separate source-code and dataset reuse terms remain unauthenticated. Article licensing is not presumed to cover every repository artifact. Full source files remain external to this note.

## Reproduction and review

Keep the nine pinned source files and `data_receipt.json` together in an external source-cache directory. Place the original audit script and independent checker beside them, then run:

```sh
python external-source-cache/reproduce_structural_audit.py
python external-source-cache/independent_csv_check.py
```

The scripts read local evidence; the first writes audit JSON beside the source files and the independent checker prints JSON. They do not download data or invoke author code. The first script requires Python's standard library and rejects changed source hashes. Its expected summary is 384 assay records, two rejected records, 381 count comparisons, 54 disagreements, one missing aggregate count and 14 complete endpoint strata. Source identities, URLs and exact hashes are recorded in the accompanying data receipt. The two scripts are original analysis; they do not reproduce the authors’ full published pipeline.

A separate AI-assisted internal reviewer independently computed all 54 disagreements and the endpoint state and raw-pattern counts; they agreed with the original audit. This is internal verification, not qualified external peer review. Before empirical modeling, obtain an authoritative version, clarify malformed records and authenticate the founder, exclusion and calibration crosswalk. No native Wsp/Aws/Mws panel or TMD validation follows from this audit.
