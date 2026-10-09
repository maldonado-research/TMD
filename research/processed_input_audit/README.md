# PTATO scoped catalogue and callability-summary audit

Mutation by Natural Dominance · R000025 · 8 October 2026, America/Los_Angeles

The official [Mendeley version 1 dataset](https://data.mendeley.com/datasets/c3r9chw9rb/1), DOI **10.17632/c3r9chw9rb.1**, now supports a checked directory topology, seven scoped file inventories and an exact arithmetic replay of three small callability summaries. **No genotype-stage numerical benchmark, independent biological truth, native origin benchmark or biological TMD fit is admitted.** The result concerns the authors' source summaries; it does not reproduce callable intervals or variant recovery.

## Official routes and bounded inventory

The cached R24 page's initial state identified `/public-api` but contained no folder records. Its linked frontend bundle establishes the versioned route `/public-api/datasets/c3r9chw9rb/folders/1` and the file-query parameters. This changed prerequisite explains the earlier unsuccessful query-version folder request. The failed route was not retried.

The official versioned route returned **477 folder records**, with 33 roots, unique IDs and paths, no missing parents and no cycles. The relevant WT, FANCCKO and MSH2KO subtrees contain 34, 21 and 31 folder records respectively, including their roots. This is the observed directory topology. It is **not a complete recursive file manifest**.

Seven explicitly scoped direct-file inventories returned **31 entries**: CallableLoci and PTATO/snvs_callable directories for each of the three cell-line groups, plus the WT multisample SMuRF directory. Each response contained fewer than the frontend's 1,000-record page size. Catalogue facts, hashes and scope are in [MANIFEST_AUDIT.json](MANIFEST_AUDIT.json). A listed file's content is not authenticated merely by its appearance in a catalogue.

The WT PTA callability BEDs are 352,180,267 and 318,212,467 bytes; the FANCC PTA BED is 509,005,097 bytes and the MSH2 PTA BED 424,829,943 bytes. The WT multisample SMuRF VCF is 21,650,223 bytes. These inputs were not fetched because they exceed the round's bounded source-response budget. Their sizes establish an acquisition constraint, not a scientific exclusion or a zero result. No full archive, raw reads or controlled EGA data was acquired.

The FANCC PTATO/snvs_callable inventory returned three summary text files and no VCF. This is a finding about that specific directory response; it does not establish absence elsewhere in the dataset.

## Three exact summary checks

Two WT PTA summaries and one MSH2 PTA summary, totaling **808 bytes**, match the official catalogue's SHA-256 hashes and sizes exactly. After parsing the response JSON and any root request/result wrapper, the `rawHtml` values contain actual tabs and newlines. They were encoded as UTF-8 without subsequent unescaping, newline normalization or content reconstruction. Raw summaries remain outside this package.

All three contain the same total of **2,875,001,522** reported state bases, including **129,814,920 REF_N** bases. Their published frequencies use the denominator **2,745,186,602**, which is the sum of the five non-REF_N states. Every count/frequency pair reproduces this convention within an absolute residual of `1e-14`.

| Table S2 label | Figure2.R recovery label | Reported CALLABLE frequency | Rounded Table S2 value |
| --- | --- | ---: | ---: |
| WT-PTA1 | WT-PTA2 | 0.86474437958808 | 0.8647444 |
| WT-PTA2 | WT-PTA1 | 0.881014499064643 | 0.8810145 |
| MSH2KO-PTA1 | MSH2KO-PTA1 | 0.774123638244392 | 0.7741236 |

The six frequencies sum to approximately **1.047288195**, because REF_N is also reported relative to the non-REF_N denominator. The five non-REF_N frequencies sum to approximately one. This demonstrated arithmetic convention does not by itself show a published error. Nor does it independently validate the denominator against reference-genome sequence, genomic intervals or variant eligibility. The precise calculations and their limits are in [CALLABILITY_AUDIT.json](CALLABILITY_AUDIT.json).

The two WT labels remain reversed in the archived clone-variant recovery plotting block relative to Table S2, as established in R24. The three acquired PTA summaries map to Training=No rows. That flag does not certify untouched evaluation, donor-level holdout or independent mutation truth. The unacquired FANCC PTA branch remains Training=Yes, as does its preceding subclone.

## Admission and reproducibility

The result advances catalogue and summary authentication while leaving every whole scientific admission gate incomplete. Variant-level CLONAL/PASS_QC and VAF membership, callable loci, filtered-header cutoffs, failures and unknown outcomes, comparison-caller records, chr17 exclusion and cross-sample CallableVariants membership remain uncomputed. The summary fractions cannot replace these inputs. Independent ancestry, inherited/pre-existing origin negatives, lost lineages and origin-catalogue completeness remain unestablished. All 26 actual study fields and 18 native control-planning fields remain unresolved; frozen models, forecasts, eta, simultaneous error allocations and the stopping rule are unchanged.

The delegate made eight logical acquisition calls and the root four: **12 total**. Delegate response captures occupy 1,659,400 bytes; root request/response wrappers occupy 79,878 bytes, for **1,739,278 saved bytes**. These serialized capture sizes include provider/MCP envelopes and sometimes duplicated representations. They are not HTTP wire-traffic measurements. Provider-internal request counts and transport-byte totals are unavailable. Exact requests, identities, source-field sizes and hashes are in [PROVENANCE.json](PROVENANCE.json).

Run the included offline checker with `--cache` pointing to the delegate's sources, `--root-cache` to the four root captures and extracted MSH2 summary, `--prior-cache` to the pinned R24 sources, and `--figure-code` to the archived `Figures/Figure2.R`. It verifies exact source pins, route evidence, directory structure, scoped inventory membership, summary authentication, denominator arithmetic and metadata mappings. [SOURCE_VERIFICATION_RECEIPT.json](SOURCE_VERIFICATION_RECEIPT.json) records the result. This internal verification is not qualified external scientific review.

Prepared by Ricardo Maldonado with AI assistance. Original documentation and derived summaries are CC BY 4.0; original checker code is MIT. The source dataset is credited to Bioinformatics van Boxtel (2023), *Comprehensive single-cell genome analysis at nucleotide resolution using the PTA Analysis Toolbox*, Mendeley Data version 1. Its own CC BY 4.0 statement includes a third-party-content caveat. Source artifacts retain their terms and remain outside Git and the public package; only the explicit [PUBLIC_FILES.json](PUBLIC_FILES.json) allowlist is proposed for publication.
