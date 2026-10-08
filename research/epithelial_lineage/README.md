# An epithelial lineage measurement lead

Mutation by Natural Dominance · R000016 · 7 October 2026, America/Los_Angeles

This round identifies a concrete published approach for linking **observed cell divisions** to newly acquired mutations while keeping survival and recovery visible. It assesses one primary study against the [cancer-domain design contract](../cancer_translation/DESIGN_CONTRACT.md). The result is a useful measurement lead and a reproducible source-stage audit. No matched TMD panel, new experiment, mutation-rate fit or cancer-prevention result is admitted.

## Selected experiment and search scope

Brody et al. (2018), *Quantification of somatic mutation flow across individual cell division events by lineage sequencing*, [10.1101/gr.238543.118](https://doi.org/10.1101/gr.238543.118), [PMC6280753](https://pmc.ncbi.nlm.nih.gov/articles/PMC6280753/).

A targeted newest-first PubMed query returned 18 indexed hits. The twelve returned metadata/abstract records were inspected; six remaining hits were not screened. Newer records concerned RNA-derived alleles, prognostic multi-omics, repeated patient sequencing, endpoint organoid profiles or conceptual models. This older primary study was selected because its optical pedigrees and explicit recovery stages match the measurement question most directly among those inspected. This is not a systematic review, a claim that no newer suitable experiment exists, or a newly discovered biological result.

All 80 main-body paragraphs, including available Methods and embedded main-figure captions, were read. Article CC BY 4.0 licensing was verified. Main-source bytes and 20 paragraph anchors are recorded in [SOURCES.json](SOURCES.json). Raw article text, reads, supplemental branch tables, figures and movies are excluded from public output. The declared supplement index's HTTPS form failed proxy CONNECT403; no unchanged retry was made. Access failure does not imply permanent source absence.

## Why this study is useful

The authors grew a short pedigree from one founding cell for each of two human cell lines, tracked divisions optically, isolated descendants, expanded subclones and jointly called mutations across their genomes. The independent imaging supplies cell-division and ancestry information that a sequence-only dendrogram cannot provide by itself. Branch variants supported by several related descendants are mapped to a lineage segment; inherited copies are not counted repeatedly as independent mutation births.

This architecture addresses a central TMD measurement problem: endpoint abundance can mix mutation production with growth and recovery. It also exposes the remaining ascertainment problem. Cells that die, fail recovery or fail outgrowth do not automatically regain known genotypes simply because the surviving cells have a well-resolved tree.

## The actual nested observation ledger

| Source stage | HT115 | RPE1 |
| --- | ---: | ---: |
|Cells in channel at collection|45|26|
|Single cells isolated|37|22|
|Subclones that grew|11|15|
|Primary subclones sequenced|11|13|
|Isolated / available|37/45|11/13|
|Outgrown / isolated|11/37|15/22|
|Sequenced / outgrown|1|13/15|
|Sequenced / available|11/45|1/2|

These are **realized descriptive fractions from nested observations**, not independent Bernoulli recovery controls, route-specific capture probabilities or biological confidence intervals. Available channel cells are not all cells ever born. The 24 primary sequenced subclones are related descendants of two displayed founders, one per background. An additional HT115 subclone provides a reference genotype; it is not a matched intervention arm or an additional cancer-validation cohort.

The stage losses partition exactly: HT115 has 8 not isolated, 26 isolated without outgrowth and 0 outgrown but unsequenced; RPE1 has 4, 7 and 2, respectively. Multiplying the three conditional stage fractions returns the sequenced/available fraction. This bookkeeping clarifies denominators without fitting a recovery model.

## What remains unmeasured for the candidate TMD test

- **Matched background:** HT115 is a POLE-proofreading-deficient colon carcinoma line; RPE1 is telomerase-immortalized retinal epithelium. Tissue, genomic background, ploidy and media differ. Their comparison cannot isolate a mutation mechanism or supply a shared-context TMD test. The source estimates HT115 predominantly diploid and RPE1 predominantly triploid; SNVs/division and SNVs/base-pair/division are different units.
- **Independent recovery truth:** the authors estimate branch-call sensitivity/specificity using consensus-lineage consistency and optical agreement, explicitly noting the lack of a sufficiently accurate independent validation method. Such caller sensitivity is not known-input cell recovery or route-specific capture. Comparing interdivision times of recovered and unrecovered cells is a useful limited bias diagnostic; it does not establish identical genotype-specific survival or detection.
- **Count law and event units:** the source observes heterogeneous accrual and related/clustered mutations. Homogeneous independent Poisson mutation counts cannot be imported unquestioned. One lesion episode can produce several correlated SNV calls; molecular events, branch calls and inherited descendants are different units.
- **Prospective cancer restriction:** no generic R1/R2/R3 catalogs, justified ordered axis, independently measured context-matched triad supply, route-specific growth/loss and recovery, or frozen held-out eta rule are supplied. Mutation signatures are not automatically those categories.

The source's approximate discussion survival percentages, exact Methods stage counts and last-decimal RPE1 caller-sensitivity difference are preserved separately in the audit/measurement ledger. No denominator repair, source software-error claim or new rate calculation is made. Source mutation-rate intervals rely on the source's own stated model; their likelihood and statistical coverage are not replayed or certified here.

## A pinned software lead

The paper's public [lineage-sequencing repository](https://github.com/yehudabrody/Lineage-sequencing---proof-of-concept) was inspected at commit `bcfe5a6c1a1407306b1c8b82e423de124e7a9f9e` (18 October 2018). Its complete six-file tree and 2,959-byte README describe Python 2.7, variant-list de-duplication, optical-lineage-constrained calls and sequence-only calls. The README's Git blob identity and the reconstructed flat Git tree match the published commit metadata.

No notebook was downloaded or executed. The mutation ZIPs were inspected as metadata only, without download or unpickling; their Git blob identifiers are not claimed to be verified byte checksums of local data. SRA and controlled comparison reads were not acquired. The primary article's CC BY 4.0 license does **not** establish the GitHub code/archive reuse license; no LICENSE file exists in the inspected pinned six-file tree. No third-party code or dataset is redistributed.

## Reproduction and next measurement step

`audit_epithelial_lineage.py` verifies the exact cached article identity, metadata/license, 20 normalized anchors, source-specific prose counts and rational nested-flow identities. It can also verify the cached commit/tree/README identities. It rejects invalid stage counts and optimized Python. It does not run the published pipeline, infer missing cell genotypes, analyze variants or estimate mutation/recovery rates.

Write outputs outside the checkout. The complete stored replay needs the four externally acquired caches:

```sh
cd research/epithelial_lineage
PYTHONDONTWRITEBYTECODE=1 python3 audit_epithelial_lineage.py --article-xml /path/to/PMC6280753.xml --pipeline-commit /path/to/pipeline_commit.json --pipeline-tree /path/to/pipeline_tree.json --pipeline-readme /path/to/pipeline_README.md --output /tmp/tmd_epithelial_lineage_replay.json --check-against AUDIT_RESULTS.json
sha256sum -c SHA256SUMS.txt
```

Without article cache, the audit explicitly reports UNRUN. Without software caches, primary-source replay can run while software replay reports UNRUN; omit the full-result comparison in that partial case. Hashes authenticate inspected bytes, not biological truth.

A qualified future study could combine independently observed pedigrees with prespecified founder/lineage sampling, matched contexts and separate known-input recovery/retention calibration. Before commissioning anything, it would still need biological review, an actual eligible route catalog, an observation model covering lost lineages and independently frozen held-out parameters. This package does not choose a partner or protocol, contact authors, register a study, allocate new statistical error or change any of the 26 unresolved bacterial study fields. Cancer-cell molecular observations do not establish clinical prevention.

Seven new source requests recorded 684,580 response bytes. Raw source bodies and data remain external. Original notes/code/derived bookkeeping were prepared by Ricardo Maldonado with AI assistance; original code MIT, original notes and summaries CC BY 4.0. No new theorem, external biological peer review or causal-force claim is made.
