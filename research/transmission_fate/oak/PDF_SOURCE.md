# Recovering the plotted oak allele counts

Plomion et al. (2018), *Oak genome reveals facets of long lifespan*, Figure 2b, report whether 19 somatic marker candidates were recovered in embryos collected from two branches of the same oak. Each marker-by-branch bar is composed of horizontal vector strokes. The caption identifies each coloured stroke as one alternate allele copy and each grey stroke as one reference copy. The upper panel is L2 (93 acorns) and the lower panel L1 (23 acorns). Published under CC BY 4.0. This derivative aggregates the strokes by marker and branch. [Paper](https://doi.org/10.1038/s41477-018-0172-3) · [Original PDF](https://pmc-oa-opendata.s3.amazonaws.com/PMC6086335.2/PMC6086335.2.pdf) · [Licence](https://creativecommons.org/licenses/by/4.0/)

The extractor uses the vector paths on page three of the checksum-verified PMC article PDF. For a local replay, install PyMuPDF (tested with 1.26.6) and run `python extract_oak.py PMC6086335.2.pdf > rebuilt.tsv`. Compare the output to `oak_alleles.tsv`. Marker order runs left to right through the nine shared-trunk, six L1 and four L2 columns. The 19 sums of reference and alternate copies each equal twice the corresponding number of accurately genotyped embryos reported in Supplementary Table 6, preserving its printed order. The row labels identify plotted markers without carrying their genomic positions. [Native Supplementary Tables 5 and 6](https://pmc-oa-opendata.s3.amazonaws.com/PMC6086335.2/41477_2018_172_MOESM1_ESM.pdf)

| Check | SHA-256 |
| --- | --- |
| Full article PDF (2,505,850 bytes) | `5e3e5544fa3fda8c1050b88aa0bdd34a2c4748c828059ae855c3558f78335856` |
| Supplement PDF (9,782,740 bytes) | `0c864f7b636641ab1ce44cc870d4448cfe53e5d484089e099bda4dbe2c6553ea` |
| Reconstructed 19-row table | `b3c31060b41910d35c4ac47dd66082bea4157b28727aab2f0fa5031408e1153f` |

Independent traversal of the full original PDF's path commands and colour states with pypdf 6.1.0 produced the identical table. The 1,348 scorable embryo-by-marker genotypes contain 294 alternate copies and 2,402 reference copies. Nine markers have at least one alternate copy. Heterozygosity alone captures seven of those markers because the scored embryos with alternate copies at the other two markers are homozygotes. These repeated measurements across overlapping embryos in one tree do not resolve the frequency of the parental lineage before fruiting, the source of each allele copy, or individual offspring haplotypes.
