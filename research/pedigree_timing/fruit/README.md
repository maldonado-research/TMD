# Repeated observations of the same plant marker across leaves and fruits

Schmitt et al. examined one *Dicorynia guianensis* and one *Sextonia rubra*. They selected crown mutations already detected in at least three leaves from fruit-bearing branches. Their paper established that rare crown variants can also appear in developing fruits. This reanalysis matches fruit measurements to leaves by marker **and physical branch**. It also measures the loss of recorded marker detections when observing fewer fruits. [Paper](https://doi.org/10.1073/pnas.2313312121) · [Supplementary Note S9](https://pmc.ncbi.nlm.nih.gov/articles/instance/10927512/bin/pnas.2313312121.sapp.pdf) · [Versioned data archive](https://doi.org/10.5281/zenodo.10089692)

## What the records show

| Observation | Dicorynia cotyledon | Sextonia embryo sac |
| --- | ---: | ---: |
| Distinct mutations called in any sampled fruit tissue | 23 | 9 |
| Distinct mutations called in the indicated tissue | 18 | 8 |
| Fruits with the indicated tissue in the archived table | 51 | 21 |
| Positive fruit-by-marker calls in that tissue | 188 | 71 |
| Positive branch-by-marker combinations on mapped branches | 46 | 24 |
| Of these, matching parental leaf call absent on that branch | **17** | **10** |
| Distinct markers contributing to those unmatched combinations | 13 | 5 |
| Unmatched / total branch-by-marker combinations at ≥20 reads and ≥3 alternate reads | 15/42 | 10/24 |

Every retained marker was recorded in the parent's leaves somewhere. For the *Dicorynia* cotyledons, **78 of 188** positive fruit-marker measurements fall on a branch with no corresponding leaf call. For the *Sextonia* embryo-sac comparison, **31 of 65** mapped positive fruit-marker measurements do so. Six additional positives come from the fruit-branch label A, which the source figure excludes. We follow the figure code for alignment of *Sextonia* branches, dropping A and mapping B to B1. All fruit observations enter the tissue-only columns above. A fruit observed on the same branch as a leaf is not that leaf's descendant. The comparison detects gaps in the spatial record of a marker. Its observations cannot independently establish a new mutation after the branch split, the first cell that carried it, or a calendar date. [Original branch mapping and fruit-table construction](https://github.com/sylvainschmitt/detectMutations/blob/252323eab5fbf994e09e11579338d462b2b5c707/README.Rmd#L269-L283)

Tissue choice changes detection even within the same fruit. In *Dicorynia*, 690 cotyledon–endocarp marker pairs had positive sequencing depth in both preparations. Both carried a positive call in 48 pairs, only the cotyledon in 78, only the endocarp in 82 and neither in 482. Another 322 pairs had zero depth in at least one tissue and 184 lacked a tissue preparation. In *Sextonia*, the corresponding counts for 179 positive-depth embryo-sac–pericarp pairs were 62, 9, 34 and 74. These comparisons refer to calls within a small roster enriched for detectable fruit markers. The source authors identify uncertainty about tissue origins and possible cross-contamination during dissection. They propose testing germinated offspring to establish inheritance more directly. [Supplementary Note S9 and Figure S36](https://pmc.ncbi.nlm.nih.gov/articles/instance/10927512/bin/pnas.2313312121.sapp.pdf)

## How much is seen when fewer fruits are read?

Suppose the archive contains $n$ fruits with a given tissue. Marker $j$ has the specified positive call in $k_j$ of those fruits. If $m$ of the archived fruits are chosen uniformly without replacement, the expected number of distinct detected markers is

$$E[D_m]=\sum_{j:k_j>0}\left[1-\frac{\binom{n-k_j}{m}}{\binom nm}\right].$$

This standard finite-population calculation requires only the observed calls. It gives every archived fruit equal weight, including a zero-depth measurement as an opportunity with no recorded detection. It averages over subsets of the actual sampled fruits. The fruits need not be independent, and their sample numbers give no temporal order.

| Archived fruits read | Dicorynia cotyledon, of 18 recoverable markers | Sextonia embryo sac, of 8 recoverable markers |
| --- | ---: | ---: |
| 1 | 3.69 | 3.38 |
| 5 | 10.19 | 4.95 |
| 10 | 13.30 | 5.90 |
| All with the tissue | 18 (51 fruits) | 8 (21 fruits) |

The smallest subset size reaching 90% of the markers observed in this tissue **in expectation** is 24 in *Dicorynia* and 17 in *Sextonia*. This is retrospective sampling coverage for two particular trees. The result supplies neither a waiting time to mutation nor a guarantee of detecting an individual event.

## Source definitions and replay

Note S9 documents **124 and 36** candidate mutations selected, 160 total. It reports that the retained multiplex assays targeted **117 and 36** respectively. The results paragraph in the main article uses 160 as the denominator in its *Dicorynia* sentence. We retain the species-specific selection and assay counts from the supplement. The deposited **filtered** fruit table contains 23 and 9 candidate sites. It supports the tissue and branch comparisons above. It omits the other candidate sites. The code used for the figure pools calls from all deposited fruit tissues when classifying sites at the species level. [Author figure code](https://github.com/sylvainschmitt/treemutation/blob/fc6a2eeef7b2bb1d178ebfbf3a79652ca13fb9df/40-Figures.Rmd#L210-L217)

We deduplicate the 7,252 *Dicorynia* and 1,722 *Sextonia* fruit rows by species, full marker identity, fruit branch, within-branch fruit number and tissue. Source preparation expands rows against parental discovery branches before exporting a reduced table. Duplicate rows give identical counts. This leaves **3,404 and 738 distinct fruit-tissue-marker measurements**. The authors' fruit call flag includes both heterozygous and alternate-homozygous genotype encodings. Our primary positive requires this flag and a positive measured alternate fraction. A leaf branch has a call if any sampled leaf on that branch carries the identical marker in the filtered leaf table. Zero listed leaf calls means no match in that table. Raw read support and per-locus callability for unlisted leaves are unavailable from that table. High-depth and alternate-count sensitivity checks apply only to fruit calls. Dated observations of ancestor and descendant cells would be required to infer a mutation's acquisition interval. [Source fruit code and table definition](https://github.com/sylvainschmitt/detectMutations/blob/252323eab5fbf994e09e11579338d462b2b5c707/README.Rmd#L252-L265)

Run `python3 -B replay.py` from this directory to regenerate `results.json` using the included tables and the Python standard library. `fruit_counts.tsv` contains the reference and alternate read counts, native sequencing depth, source call flag, and sample metadata. `leaf_calls.tsv` records leaf-call counts by marker and branch. Marker IDs sort the selected sites separately for each tree. Native tissue spellings are preserved. To verify the extraction, run the following from this directory.

```sh
python3 -B fetch_sources.py native
python3 -B extract.py native regenerated
cmp regenerated/fruit_counts.tsv fruit_counts.tsv
cmp regenerated/leaf_calls.tsv leaf_calls.tsv
python3 -B replay.py --directory regenerated | diff - results.json
```

The fetcher retrieves the compressed payloads of three members from the 4,239,118,097-byte Zenodo ZIP using byte ranges. It checks each decompressed member against its SHA-256. The same files can be extracted from the full original archive. Download ranges, member paths and digests are in the fetcher. The source archive credits Sylvain Schmitt, Thibault Leroy, Myriam Heuertz and Niklas Tysklind. The source archive carries the Creative Commons Attribution 4.0 license. [Data and licensing](https://zenodo.org/records/10089692) · [Code release](https://doi.org/10.5281/zenodo.10090430)

For an independent check of the fruit-table counts, extract the two `*_candidate_fruit_mutations.vcf.gz` files from the archive's `treemutation_save/02_mutations/04_fruits/` directory into `native/`. Run `python3 -B verify_vcf.py native | diff - vcf_receipt.json`. This matches the reference count, alternate count, depth and source call flag in all 4,142 records. The source VCFs include nine alternate-homozygous genotypes for *Dicorynia* and one for *Sextonia* among the published markers.
