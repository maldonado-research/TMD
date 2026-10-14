# R36: what the actual supplement resolves

The previously uninspected [supplement to Tourlousse et al.](https://pmc.ncbi.nlm.nih.gov/articles/instance/11912825/bin/tourlousse_supplement_ycaf028.pdf) clarifies the processing provenance of the retained soil-mass data: **Figure S3 uses random subsampling to 60,000 reads, and Table S5 specifies primer-dependent preprocessing settings.** A targeted check of the already authenticated source tables finds that all 22 Figure S3 rows total exactly 60,000 reads; the corresponding Figure 2D totals range from 62,909 to 151,648. These are different processed count representations, consistent with the supplement caption.

The supplement does **not** resolve the physical extraction/PCR/library genealogy, exact introduced dose or dose uncertainty, or accession-specific exclusions for the frozen 22 retained plus two candidate-library frame. All 72 literal run/experiment/library queries return zero matches in its extracted text. The two candidate runs remain SRR30280226 and SRR30280227; their processed standard counts and individual exclusion decisions remain unknown. Released records still do not establish the full attempted-sample denominator.

## Acquisition depth and evidence limits

The selection, literal joins and admission rules were [declared before acquisition](PRESPECIFICATION.md). Firecrawl reports successful processing of all **18 of 18 pages** of the named PDF. Its complete response is retained externally, with byte identity and acquisition details in [source provenance](SOURCE_PROVENANCE.json). The representation contains Supplementary Note 1, Figures S1–S11 and Tables S1–S5. Table S1 describes constructs, S2 their sequences, S3 the primers, S4 primer binding/amplicon details and S5 read-processing settings.

An additional exact-URL GET returned a 1,816-byte HTML download/proof-of-work interstitial with HTTP 200, rather than PDF bytes. No challenge was solved. Consequently **the local original PDF and page images were not authenticated**: supplement statements below are verified within the captured Firecrawl text representation, not by visual inspection or a local PDF byte hash. The provider's automatically generated numerical tables for plotted figures are excluded from the analysis. Exact source-count checks use the previously authenticated TSV members, not plotted points or provider-generated plot values. Negative findings are bounded by this representation and the prior frozen source records, not proof that undisclosed records do not exist.

## A resolved distinction between Figures S3 and 2D

The Figure S3 caption states that its count tables were randomly subsampled to 60,000 reads. A post-capture exploratory consistency check sums the twelve rDNA-mimic count columns and the environmental count column for every retained row in the original `data/figureS3.tsv` and `data/figure2D.tsv` members of the [author data release](https://doi.org/10.5281/zenodo.14592209).

| Source-table check | Result |
| --- | --- |
| Retained run identifiers | Same 22 SRRs in both tables |
| Figure S3 aggregate reads | Exactly 60,000 for every row |
| Figure 2D aggregate reads | 62,909–151,648; all 22 above 60,000 |
| Primer labels | All agree |
| Literal mass labels | Six rows retain the known 37 versus 37.5 discrepancy |

The [count-total audit](COUNT_TOTAL_AUDIT.json) contains original derived totals and exact run identifiers. This corroborates the stated subsampling level; it does not recover the random seed or prove the exact parent-to-subsample transformation. No random draw, new regression, source performance estimate or native biological inference is computed. The R34 replay continues to use its original Figure 2D counts and declared 37-mg predictor. Neither source mass label is promoted to actual weighed mass.

## Newly inspected processing settings

The following is an original selected synthesis of Table S5's reported settings for the three target primer sets. These are protocol specifications, not a run-level execution log or an accession-specific QC decision.

| Target primer | Cutadapt minimum length, bases | DADA2 truncation length, bases | DADA2 maximum expected errors |
| --- | ---: | --- | --- |
| SSU-V4 | 225 | 150 for each paired read | 4 for each paired read |
| ITS1 | 185 | No explicit value shown | 4 |
| ITS2 | 225 | 225 | 4 |

All three commands report removal of reads lacking required primer matches and a maximum ambiguous-base count of zero. The reused primary methods explain that ITS1/ITS2 analysis uses forward reads, whereas V4 uses separately denoised forward/reverse reads followed by merging. These settings help locate processing stages between released sequencing reads and final standard counts. They do not reveal how many reads either candidate lost at each stage, whether the recorded settings were actually used for a particular run, or the statistical distribution of biological detection loss. No author command is executed.

Figure S9's separate less-than-ten-read rule applies to bacterial/fungal **mock-community strain** abundance estimates used in pairwise comparisons. It is not an accession-specific explanation of the soil 300-mg V4 rDNA-mimic omission. The primary article's condition-level exclusion remains distinct from that rule and from Table S5's read-level filters.

## What remains unresolved

The [supplement audit](SUPPLEMENT_AUDIT.json) screens each of the 24 released condition-label records by its exact SRR, SRX and library label. Its zero matches provide no additional physical preparation links. A shared BioSample, distinct library suffixes, generic replicate language and final sequencing pooling still cannot identify independent extractions or biological units.

The reused primary methods report fluorometric plasmid-DNA quantification, dilution to a nominal 10 ng/µl stock, two-step PCR and an approximately four-million-copy mixture introduced after bead-beating lysis for the varying-soil experiment. Those source-level descriptions do not provide run-linked measured stock concentration, dilution/pipetting uncertainty, input volume, introduced copy count or a covariance structure. The supplement supplies primer/construct information, not that missing measurement ledger. No nominal stock or molecular count is substituted for viable cells, native mutation births or pre-entry recovery.

Supplementary Note 1 derives conditional ALR relationships by starting from equality between absolute-abundance ratios and read-count ratios and holding specified amounts fixed by design. This is a stated modeling premise and algebraic consequence, not a new empirical measurement of unbiased recovery or a validated biological count law for TMD.

The [decision](DECISION.json) therefore admits source-processing clarification only. All 26 study and 18 planning fields remain null; no native stock, independent mutation event, matched panel, native calibration, native biological fit or new theorem is admitted. Frozen R5/R11/R17, theta/eta forecasts, comparators, evaluation, error allocation, stopping, paused runner and methods 0.6.0 are unchanged.

## Reproduction and rights

[Original Python](replay_supplement.py) verifies packaged hashes and frozen dependencies without network access or file writes. A public-only run explicitly reports source replay **UNRUN**. Supplying the external capture directory and reused source archive reproduces literal identifier screening, selected Table S5 parameter parsing and the original-table count-total audit:

```sh
python research/calibration_supplement_records/replay_supplement.py
python research/calibration_supplement_records/replay_supplement.py --source-cache EXTERNAL_CAPTURE_DIRECTORY --data-archive EXTERNAL_DATA_ARCHIVE
```

Two supplement acquisition attempts produced one usable source representation and one HTML interstitial. Saved acquisition files total **169,527 bytes**; a redundant extracted-text convenience copy adds 76,316 bytes, for **245,843 total locally saved source/representation bytes**. Reused R33/R34/R35 sources add no new scientific acquisition. Both totals remain below the 8-MiB worker cap. A separate root-requested native-preprint PDF attempt returned HTTP 429 and acquired no PDF body; its receipts are accounted separately in source provenance. Total worker acquisitions: three. Provider-internal/wire bytes are unknown. No FASTQ, new author source code, project/author Zenodo request, outreach or laboratory work occurs.

The main article displays CC BY 4.0; separately marked supplement material and other third-party rights are not assumed to inherit that license. No separate license statement was found in the extracted supplement representation. Raw PDF substitutes, sequence tables, full tables, page captures, contact details and author code are excluded from this public package. Original report and synthesized audits: CC BY 4.0; original Python: MIT. Attribution: Ricardo Maldonado with AI assistance; source facts attributed to Tourlousse et al., DOI [10.1093/ismeco/ycaf028](https://doi.org/10.1093/ismeco/ycaf028), and the cited author data release. This is a source/computational assessment, not qualified external biological validation.
