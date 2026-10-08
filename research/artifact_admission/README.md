# R23: PTATO official-artifact admission assessment

The official article, two published software records, an archived figure-code ZIP and a pinned tool-source inventory were inspected. **No numerical variant benchmark or native new-origin benchmark is admitted.** This advances the historical DESCRIPTION_ONLY worksheet to ARTIFACT_INSPECTED_NO_NUMERICAL_BENCHMARK_ADMITTED. Missing processed data, metadata workbooks, experiment-to-release mapping and independent origin truth remain explicit. Qualified external biological/statistical review has not been obtained.

The scope is 12 scientific HTTP requests, 479,974 response bytes, 22 selected complete article paragraphs and selected code sections. One initial sandbox failure occurred before any HTTP request could leave. This is a bounded inspection, not a full-paper, full-pipeline or raw-data reanalysis. No raw sequencing was downloaded, no new biological observation was made and no remote object was changed.

## Verified artifact identities

The [article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10504672/) is DOI 10.1016/j.xgen.2023.100389. Reacquired XML is byte-identical to the R21 source (223,535 bytes; SHA256 2653d1945c445ae63b23b3be068f66b294e60c3e4d680c679254283b6a4722e5). That establishes identity, not new independent scientific evidence.

Its key-resources table names raw WGS accession **EGAS00001007288**, processed somatic variants/western blots [Mendeley version 1](https://doi.org/10.17632/c3r9chw9rb.1), and reused PTA-source study **SRP178894**. These are verified article pointers; release manifest, experiment/sample mapping and artifact-specific reuse/privacy conditions for the biological datasets were not acquired. The EGA and Mendeley hosts are outside the inspected effective network allowlist. No request to those hosts was made and no access condition was inferred from the article license.

The paper-linked [tool release](https://zenodo.org/records/8098608) is **ToolsVanBox/PTATO v.1.2.4**, published 30 June 2023. Its public record lists one 361,371,002-byte ZIP, metadata MD5 24a61a7fa325f29babf11586150a3e2d. The archive exceeds the bounded download cap and was not downloaded. A non-truncated GitHub tree for that tag identifies 154 blobs, with Git object identifiers and listed byte sizes. Four small source blobs were acquired and their content verified against Git blob SHA1. This is a source inventory, not the complete biological-data manifest.

The paper-linked [figure-analysis release](https://zenodo.org/records/8186323) is **ProjectsVanBox/PTATO v1.0.1**, published 26 July 2023. Its ZIP was acquired: 94,579 bytes, SHA256 51ee4dc35697ccc3dce9beacae9e85479399b59cb2e03bc166a3c00ad844d33a. Its MD5 matches the public record. The 18 archive entries comprise two directories and 16 files; there are 14 R files plus README and LICENSE. The archive supplies scripts, not the required Table_S2.txt, VCF, BED or other biological inputs. Both inspected software LICENSE files say MIT. Article CC BY 4.0 does not supply the uninspected biological-data license.

Two PMC supplement requests for Table S1 and Table S2 returned HTTP 200 with Google reCAPTCHA HTML. Neither response is an XLSX ZIP. Their false filename suffixes and HTTP statuses are not evidence of workbook acquisition. No unchanged retry was made.

## Labels and denominators

Article paragraph 98 (XML p0305) defines training positives using shared PTA/bulk calls from specified donors/cell lines, and artifact labels using linked-read score <1 or low expected cord-blood mutation burden. Discordant shared/linked-read cases and copy-number/LOH regions are excluded. Paragraph 99 (p0310) excludes <5% of variants with missing allele-balance/replication-time features from the principal training. These are selected genotype-stage labels, with proxy artifact labels in some groups. They do not independently establish every variant's ancestry or acquisition episode. Unknown origin truth remains unknown.

Paragraph 18 (p0090) states that additional AML donors and cord blood were outside training, but the in-silico experiments recombine selected feature records and modify sequence contexts. An out-of-training donor is useful separation; it does not make synthetic mixtures independent biological trials or prove an untouched native-system evaluation.

The Figure2.R artifact confirms additional conditioning. At lines 1386–1409, variants in the preceding clone must be labelled CLONAL/PASS_QC by SMuRF and pass the VAF cutoff. At lines 1439–1451, PTA outcome classes are overwritten by FAIL_QC and LOW_COV. At line 1459 chromosome 17 is excluded because SCAN2 did not run there. At lines 1527–1533, summary bars average per-sample frequencies and separately sum displayed denominators. They are not pooled estimates from independent cells or origins.

At line 1555, `CallableVariants` is built from the **variant-name set** among PTATO PASS/FAIL rows across samples. The following subsets use membership in that set and then group by sample ID. The effect of repeated loci across samples on the sample-specific eligible frame needs the actual inputs. This is a concrete unresolved reproducibility check, not a demonstrated numerical error. The code and its inputs must be audited together before reproducing the reported denominator.

Consequently, the article's 45–69% shared-substitution recovery and 86.8% average sensitivity for detectable substitutions are retained only as accurately conditioned published reports (paragraph 33, p0100). They were not recomputed or multiplied to form origin inclusion. Article paragraphs 19 and 73 explicitly note unknown exact artifact counts and signature-refit estimates. Figure2.R lines 901–967 execute a signature bootstrap/refit; that calculation does not add an independently labelled negative catalogue.

## Ancestry, missingness and dependence

Figure2.R lines 233–244 construct presence from SMuRF CLONAL_SAMPLE_NAMES and mark FAIL_QC samples NA. Lines 283–294 select candidates unique among preceding columns with `rowSums(..., na.rm = TRUE) == 1`. Thus observed call patterns and column order are used to classify when candidates appear. Earlier missing genotype states are omitted in that calculation; they are not independently verified negatives. The code comment calling these mutations post-clonal-step is not independent acquisition-episode truth.

The four displayed PTA sample groups at lines 1462–1466 are WT PTA1, WT PTA2, FANCC knockout PTA1 and MSH2 knockout PTA1. They derive from nested expanded AHH-1 cultures. The repair backgrounds differ and two observations share the WT background; four plotted groups are not demonstrated four independent founder histories. Table S2 is necessary to authenticate the complete clone/culture/batch relationships, days, exclusions and failed samples.

Neither the inspected figure-code archive nor the selected methods supplies optical pedigrees, independent inherited/pre-existing variant negatives, genotypes of lost/nonexpanding cells, all-birth inclusion probabilities or a complete origin catalogue. Clone-level expected burdens per culture day are not observed division denominators. Reused SRP178894/ENU observations do not become a new biological experiment when reanalyzed by PTATO.

## Caller freezing and transfer

The article reports GRCh38, BWA 0.7.17, GATK 4.1.3.0, NF-IAP 1.3.0, SMuRF filters, GATK CallableLoci 3.8.1 and sample-adaptive PTATO cutoffs (paragraphs 15, 86, 91, 103, 105 and 107). The archived tool README confirms that raw short-variant calling precedes PTATO, with at least a germline bulk control and a multi-sample input VCF. Reference FASTA and SHAPEIT resources are separate downloads. The source tree identifies the RF model and indel exclusion-list objects, but their bytes were not acquired.

The paper's key-resources table and methods report different Sambamba versions (0.8.2 and 0.6.8). This inspection preserves that difference; it does not silently choose the study's actual runtime. The inspected process config includes SMuRF 3.0.1 and 3.0.2 labels and resource/config options; complete actual execution settings, logs, image digests and reference-resource hashes remain unverified. A published software release is not an authenticated per-sample execution record.

Freezing must include the complete upstream caller, reference and control files, trained model, recurrence filters, callability/QC rules, linked-read/spectrum adaptation algorithm and resulting per-sample settings. No matching/transport to a specified native TMD system has been justified. All 26 actual bacterial registry values remain unresolved; no W/A/M qualifying-route count law, native pi, mutation production per division, biological TMD fit or cancer-prevention result follows from this inspection.

## Next concrete evidence

The next useful acquisition is the official version-1 processed-data manifest and eligible bounded files, Table S2 in authentic workbook/text form, and a sample-to-clone/culture/release map. First replay the genotype-stage conditional recovery categories, including chromosome 17 exclusions and the cross-sample `CallableVariants` membership rule. Native origin admission additionally requires independently generated ancestry/episode truth, inherited/pre-existing origin-negative variants, lost-lineage limits and a justified target-system design. Qualified biological/statistical assessment of those facts remains outstanding.

The accompanying JSON ledger maps each of the nine original admission gates to verified evidence and missing conditions. Public outputs contain original analysis and provenance. Article bodies, external source code, biological data and challenge HTML remain outside the public package.

## Reproduction and reuse

Run `python3 -B verify_cached_sources.py --cache /path/to/external/sources` and `sha256sum -c SHA256SUMS.txt`. The cache must contain the exact pinned source filenames. A missing cache prevents source replay; package hash checks cannot substitute for it. The checker prints a receipt and never fetches or writes source data.

The recovered [admission worksheet](WORKSHEET.md) preserves the starting gates. [Hypothetical control-resource calculations](../control_resource/README.md) remain separate from this source assessment. Prepared by Ricardo Maldonado with AI assistance. Original checker code is MIT; original documentation, manifests and summaries are CC BY 4.0. External sources retain their terms and are not redistributed. Internal review does not replace qualified external scientific assessment.
