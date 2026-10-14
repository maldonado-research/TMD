# R35: accession provenance after the Figure 2D replay

All 22 retained Figure 2D run accessions now join exactly to authoritative SRA experiment and library labels. They share the submitted sample identifiers **SRS22380613 / [SAMN43151561](https://www.ncbi.nlm.nih.gov/biosample/SAMN43151561)**. Two additional archived runs explicitly name the missing V4 300-mg condition. This resolves archive identifiers and narrows the candidate omission to named runs. It does not resolve extraction ancestry, biological independence, exact introduced dose or the full attempted-sample denominator.

The question and join rules were [declared before inspecting experiment records](PRESPECIFICATION.md). This continues the provenance question left by the [R34 processed-count replay](../calibration_source_replay/REPORT.md); it adds no regression, figure or mathematical extension.

| Question | Evidence obtained | Remaining limit |
| --- | --- | --- |
| Which archive records represent the 22 retained rows? | 22 exact SRR joins, 22 distinct SRX experiments and 22 distinct library names; no unmatched, duplicate or Figure 2D primer/mass conflict | Archive experiment/library identifiers do not establish separate physical preparation events |
| Which submitted sample labels do they share? | All 22 point to SRS22380613 / SAMN43151561, titled `soil_rDNAmimics` | A shared annotation does not establish one physical specimen, one extraction, a common biological ancestor or independent biological units |
| Which archived runs name V4 at 300 mg? | SRR30280226 and SRR30280227 | Candidate omitted-condition runs; their individual exclusion reason and processed standard counts remain unverified |
| Is exact soil mass consistent across deposited artifacts? | Six low-soil rows say 37 mg in Figure 2D and SRA library labels but 37.5 mg in Figure S3 | Actual weighed amounts are unresolved; R34's declared 37-mg predictor is preserved |
| Are exact dose and replicate ancestry recovered? | No row-level measured dose, uncertainty, extraction or biological replicate ledger found | These fields remain null |

## Authoritative metadata and exact joins

The official [BioProject PRJNA1100950](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1100950) page reports 178 SRA experiments and eight BioSamples. A complete eSearch result returned 178 identifiers; one exact eFetch XML response returned 178 experiment packages and 178 distinct run records. This count describes the public archive response on 14 October 2026. It does not count independent experiments in a biological sense or every sample ever attempted.

The [accession join](JOIN_AUDIT.json) records the selected identifier fields for every retained row. It also checks run-to-experiment and experiment-to-sample cross-references. Experiment title, alias and library name agree for the selected soil-mass records. The library names explicitly encode primer and nominal soil amount and agree with the fixed Figure 2D labels. Their `S` suffixes distinguish submitted library labels but have no documented extraction or biological replicate meaning in the examined metadata.

All 24 project records with the anchored soil-mass/mix-E library-name pattern use the same SRA sample and BioSample identifiers. The BioSample has collection date, geographic location, isolation source and isolate marked “not applicable,” with latitude/longitude “missing.” The SRA XML's `Pool`/`Member` elements repeat its sample annotation; they do not provide an experimental physical pooling or ancestry ledger. General paper-level library pooling instructions and the technical-replicate language for other figures cannot fill this Figure 2D-specific gap.

## Two named candidates for the omitted condition

| Run | Experiment | Submitted library label |
| --- | --- | --- |
| [SRR30280226](https://www.ncbi.nlm.nih.gov/sra/SRR30280226) | SRX25741059 | `V4_soil300mgmixE_S16` |
| [SRR30280227](https://www.ncbi.nlm.nih.gov/sra/SRR30280227) | SRX25741058 | `V4_soil300mgmixE_S15` |

Both are absent from the retained Figure 2D table. The [primary article](https://doi.org/10.1093/ismeco/ycaf028), reused from R33, says the 300-mg V4 condition was excluded because it yielded fewer than ten rDNA-mimic reads. That condition-level statement makes these two named runs plausible omitted-condition candidates. It does not authenticate a per-run processed count or an accession-specific exclusion decision. An independent search of all 94 substantive previously archived members, including all 16 XLSX workbooks' XML components, found neither candidate's exact SRR, SRX or library label. No additional processed counts or exclusion ledger were recovered.

There are 24 released records with the declared soil-mass pattern, of which 22 occur in Figure 2D. This is a public-record subset, **not a recovered denominator of 24 attempted biological samples**. Unsubmitted, failed, pooled or otherwise undocumented preparations cannot be counted from this difference. SRA sequencing totals do not measure denoised rDNA-mimic counts. No detection probability, invisible-loss bound or new filtering decision follows.

## Dose and mass limits

The primary article reports a constant approximate dose of four million total rDNA-mimic copies for the varying-soil experiment, added after cell lysis by bead-beating. This remains an author methods claim. Neither the structured experiment records nor the BioSample page supplies exact per-accession introduced copies, dilution/concentration uncertainty or actual weighed soil mass. The archive identifiers do not turn gene-copy read ratios into viable-cell counts, recovery fractions or native TMD input quantities.

The six shared low-soil accessions are SRR30280192, SRR30280203, SRR30280223, SRR30280224, SRR30280326 and SRR30280337. Their mass label is 37 in Figure 2D, Figures 2E/S4/S5, SRA library names and the main-text condition list, but 37.5 in Figure S3. Figure S3 uses the same accession set with different processed counts. We preserve those literal labels and the discrepancy; neither figure's label is silently promoted to exact physical truth. No refit or change to the R34 replay is made.

## Reproduction, accounting and preservation

[Original Python code](replay_provenance.py) reconstructs the exact identifier joins from authenticated XML and two selected members of the existing data archive. It uses standard-library parsing, writes no files, makes no network requests and executes no author code. A public-only invocation checks package integrity, recorded scope and frozen dependencies; source replay is explicitly **UNRUN** unless the external captures and original archive are supplied:

```sh
python research/calibration_sample_provenance/replay_provenance.py
python research/calibration_sample_provenance/replay_provenance.py --source-cache EXTERNAL_CAPTURE_DIRECTORY --data-archive EXTERNAL_DATA_ARCHIVE
```

[Source provenance](SOURCE_PROVENANCE.json) records exact byte lengths, SHA-256 identities and acquisition scope. Five conservative acquisition attempts produced four successful scientific responses: two Firecrawl page captures, one eSearch JSON and one SRA XML. The failed local sandbox attempt acquired zero response bytes. Total saved source material is **1,536,860 bytes**: 1,500,664 original structured-response bytes, 29,275 bytes of complete Firecrawl request/result wrappers and 6,921 receipt bytes. Prior R33/R34 evidence is reused without new acquisition. This remains below the five-attempt and 8-MiB worker caps.

The raw XML contains submission contact and postal details and remains outside Git, as do all raw source tables, page captures and archives. The public package contains selected public identifier joins and original synthesis. The independent reviewer checked the source joins, cross-references, omission candidates, mass discrepancy and archive-search limitations. This is a computational/source review, not a qualified external biological review.

All 26 study fields and 18 planning fields remain null. No native stock, independent mutation event, calibration record, matched panel, native biological fit or new theorem is admitted. Frozen R5/R11/R17, theta/eta forecasts, comparators, error allocation, stopping, paused runner and methods 0.6.0 remain unchanged. The next informative evidence would be a row-linked preparation/ancestry ledger, introduced-copy measurements with uncertainty and a complete attempted-sample/exclusion record.

Original assessment and synthesized joins: CC BY 4.0. Original Python: MIT. Ricardo Maldonado with AI assistance. Third-party rights remain unchanged; public NCBI access is not treated as a CC license or patent-use permission.
