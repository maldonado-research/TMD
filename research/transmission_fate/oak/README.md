# Somatic mutations in oak buds and genotypes in acorn embryos

Plomion et al. genotyped embryonic radicles and plumules from 116 acorns of one pedunculate oak. Nine of 19 amplified parental markers appeared in at least one embryo. A later study reported parental allele fractions for exactly those nine markers. All ten markers without an observed carrier lack parental fractions in that table. A forecast from the published parental fractions across the full panel is therefore unscorable. [Plomion et al., 2018](https://doi.org/10.1038/s41477-018-0172-3) · [Xian et al., 2025](https://doi.org/10.1093/g3journal/jkaf143)

## Reconstructing the embryo outcomes

Of 21 parental somatic markers selected for the assay, 19 amplified and two failed. The acorns came from branch L1 (23) and L2 (93). Supplementary Table 6 reports the number of callable embryos and heterozygosity for each marker. Figure 2b gives the number of alternate and reference allele copies in each branch's embryos. Matching the figure columns to the assay table reproduces the callable denominator of every amplified marker. All 19 identifiers also match Xian et al. Table S8. The parental origin category comes from Plomion et al. Tables 5 and 6. The former's allele-frequency column describes pooled sequencing from other oak trees. [Original supplement, Tables 5–6](https://static-content.springer.com/esm/art%3A10.1038%2Fs41477-018-0172-3/MediaObjects/41477_2018_172_MOESM1_ESM.pdf) · [Figure 2b](https://www.nature.com/articles/s41477-018-0172-3/figures/2) · [Xian et al. supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC12341919.1/jkaf143_supplementary_data.zip)

| Parent origin assigned by the authors | Attempted | Amplified | Detected in at least one embryo |
|---|---:|---:|---:|
| Between branch initiation sites XL1 and XL2 | 9 | 9 | 5 |
| L1 branch | 8 | 6 | 4 |
| L2 branch | 4 | 4 | 0 |

Let $A$ be the pooled alternate-copy count at a marker and $h$ its heterozygote count. We recovered $h$ as the unique integer compatible with the published three-decimal heterozygosity and callable count. Diploid genotype accounting then gives $(A-h)/2$ alternate homozygotes and $(A+h)/2$ carriers. Two loci with zero heterozygosity had alternate copies. At those loci the alternate calls came entirely from homozygous embryos. [Joined marker counts](marker_counts.tsv)

Among the 1,348 genotyped marker–embryo pairs, 62 were heterozygous and 116 homozygous alternate, for **178 carrier calls (13.20%)**. The same embryos and loci occur repeatedly. With 856 missing genotypes, the carrier proportion across all 2,204 possible pairs ranges from **178/2,204 to 1,034/2,204 (8.08% to 46.91%)**, allowing each missing genotype to be absent or present. At an individual amplified marker with $k$ observed carriers and $n$ genotyped embryos, the corresponding limits are $k/116$ and $(k+116-n)/116$. Every amplified marker has at least three missing genotypes, so the number of distinct markers present somewhere in all 116 embryos lies between 9 and 19. The two failed assays supply a further 232 unobserved marker–embryo pairs outside the amplified panel. [Complete counts and bounds](results.json)

**Parental origin of an allele.** Under ordinary diploid Mendelian inheritance, with one maternal and one paternal copy, correct calls and no new mutation, an alternate homozygote must carry a maternal alternate. The parental origin of a heterozygote's alternate copy is ambiguous. Across the full 19-marker grid, the resulting marginal range for maternal alternate transmission is **116/2,204 to 1,034/2,204**. For marker 11, its 55 alternate homozygotes, 12 heterozygotes, 41 reference homozygotes and eight missing embryos permit **55 to 75 maternal transmissions among 116 acorns**. The authors estimated approximately 44% selfing from control loci and report high missingness. A same-tree pollen contribution is plausible. These marginal bounds use no linkage, phased parent-of-origin information or constraints shared across markers. [Study methods](https://doi.org/10.1038/s41477-018-0172-3)

## Exploratory branch comparison

After inspecting the source margins, we compared all ten amplified markers assigned to L1 or L2. The nine markers placed between XL1 and XL2 lack a single branch label for this comparison. The difference for a marker is its **embryo alternate-copy fraction on the assigned branch minus that on the other branch**. Each marker has a nonzero callable denominator on each branch.

For branch $b$ with $N_b$ sampled embryos, $A_b$ alternate copies and $R_b$ reference copies, the called fraction is $A_b/(A_b+R_b)$. The all-embryo fraction is between $A_b/(2N_b)$ and $1-R_b/(2N_b)$. Subtract the other branch's upper endpoint from the assigned branch's lower endpoint for the minimum difference. Reverse the extrema for the maximum. Giving every marker equal weight gives a called-case mean of **+10.47 percentage points**. Over all 23 L1 and 93 L2 embryos, the mean ranges from **−38.32 to +43.71 points**. These endpoints are attained when each missing genotype may independently contribute zero, one or two alternate copies. They describe compatibility with the recorded data and impose no cross-marker linkage constraints. [All ten marker contrasts](branch_contrasts.tsv)

Two of the ten retain a strict direction under every such completion. Marker 12 favors its assigned L1 branch by **+4.35 to +21.74 points**. Marker 11 has a smaller fraction on its assigned L1 branch by **0.51 to 9.12 points**. It contributed 24/46 alternate allele copies on L1 and 98/170 among called copies on L2. Even if every missing L2 genotype were reference, the L2 fraction would be 98/186. Its alternate-copy majority in the embryos survives every completion, while its maternal transmission interval spans one half. Six of the ten branch-specific markers had zero alternate copies anywhere among called embryos. Branch labels identify the authors’ inferred parental origin region. Acorn pollen parentage, dates of mutation, unobserved parental mosaicism, and selective establishment remain unresolved. [Marker counts](marker_counts.tsv) · [Source figure](https://www.nature.com/articles/s41477-018-0172-3/figures/2)

## Reproduction

The `figure_order` identifier follows Figure 2b, and `s6_order` is the somatic-marker order in Supplementary Table 6, including the two failed assays. The value `shared_trunk` denotes the source interval between XL1 and XL2. It denotes a position on the main stem. We do not use it to assign a transmitting branch. For the two failed assays, NA denotes an unavailable observation. [Figure extraction and source hashes](PDF_SOURCE.md)

Run from this directory with Python 3.10 or later. Offline replay uses only the Python standard library.

```sh
python3 -B audit_oak.py | diff - results.json
python3 -B audit_oak.py --branch-tsv | diff - branch_contrasts.tsv
```

For a source-level replay, use the PMC version 2 article PDF, the original Table 5/6 supplement and the Table S8 workbook extracted from Xian et al.'s journal ZIP. Figure extraction uses PyMuPDF and supplement extraction uses Poppler's `pdftotext`. The scripts check the source hashes and reconcile branch counts, callability and recovery flags before printing. A separate parser verified every plotted allele count. The journal ZIP's SHA-256 is `21379397a16827e01b05b68583eb352de651fdddd58162ea727e500858b13923`. [Article PDF](https://pmc-oa-opendata.s3.amazonaws.com/PMC6086335.2/PMC6086335.2.pdf) · [Plomion supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC6086335.2/41477_2018_172_MOESM1_ESM.pdf) · [Xian supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC12341919.1/jkaf143_supplementary_data.zip)

```sh
python3 -B extract_oak.py /path/to/PMC6086335.2.pdf > /tmp/oak-alleles.tsv
cmp /tmp/oak-alleles.tsv oak_alleles.tsv
python3 -B extract_markers.py /path/to/41477_2018_172_MOESM1_ESM.pdf /path/to/Supplementary_Tables_G3-2025-405931.xlsx --alleles /tmp/oak-alleles.tsv | diff - marker_counts.tsv
```

The derived table aggregates data published by Christophe Plomion and coauthors under CC BY 4.0 and records the availability of the later parental measurements tabulated by Xian and coauthors. [Original article and license](https://doi.org/10.1038/s41477-018-0172-3) · [Later study](https://doi.org/10.1093/g3journal/jkaf143) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
