# What the physical peach-tree diagram establishes

Wang et al. drew the young DHQ1 peach tree with four main axes, B1–B4, and annotated the smaller shoots with location codes such as B1-1 and B4-1-3. We transcribed the diagram’s labels, then matched them to the sample names in S1 Data. Removing the terminal leaf identifier (L1 or L2) maps 75 samples to 46 named locations. Two leaves assigned the same location can occupy different positions near the attachment. The geographic drawing does not establish which cells founded a leaf. The paper’s Results and caption give different months for the 2016 leaf collection, so this analysis uses the year. [Primary paper and Figure 4](https://doi.org/10.1371/journal.pbio.3000191.g004) · [Sample roster, S1 Data](https://doi.org/10.1371/journal.pbio.3000191.s018)

| Primary branch | B1 | B2 | B3 | B4 |
|---|---:|---:|---:|---:|
| Sampled leaves | 29 | 33 | 6 | 7 |
| Distinct sites listed in its leaves | 13 | 18 | 9 | 8 |

All 48 reported sites have carriers in just one primary branch, reproducing the authors’ observation. Branch topology informed candidate discovery. Their second, frequency-based screen could prompt correction of suspected recording mistakes. The anatomical labels and the reported mutation inventory therefore cannot serve as independent validation of one another. The published author repository supplies the detection workflow. Its listed somatic-mutation directory contains no DHQ1 tree file. [Published Methods and Figure S1](https://doi.org/10.1371/journal.pbio.3000191.s001) · [Mutation inventory, S2 Data](https://doi.org/10.1371/journal.pbio.3000191.s019) · [Author workflow](https://github.com/wl13/BioPipelines/tree/bac1d4bcfe4c784378a1cee8823ced9943bd4482/Mutation_Detection/Somatic_Mutations)

## Two ways of counting the same sites

Fourteen sites occur in two or more leaves. For three of them, both leaves share one location code (B1-1, B2-11 and B2-15). The remaining 11 span multiple locations on the same main axis. The authors assigned their 11 shared mutations to 2015 and the remainder to 2016 using their developmental assumptions. Counting carrier leaves reproduces their first- and second-year measurements exactly. [Figure 4 and original reported totals](https://doi.org/10.1371/journal.pbio.3000191)

| Observed carrier distribution | Distinct sites | Site–leaf occurrences | Occurrences per sampled leaf |
|---|---:|---:|---:|
| Multiple named locations | 11 | 108 | 1.44 |
| One named location | 37 | 40 | 0.5333 |

The multi-location group leads when each site contributes once for every leaf carrying it. The one-location group leads when each distinct site contributes once. Give the first carrier of each site weight 1 and every additional carrier weight λ. The sums become 11 + 97λ and 37 + 3λ. Their ordering switches at λ = 13/47 (about 0.277). This calculation identifies the observational unit behind the apparent ordering. It supplies no branch-time or cell-division denominator from which to estimate an annual formation rate. [Computational receipt](physical_groups.json)

## The 27, 14 and eight carriers in B1

Wang et al. highlighted mutations 1, 2 and 3 in their diagram as evidence of hierarchical cell divisions. They occur in 27, 14 and eight of the 29 B1 leaves. The carrier lists give six patterns when these mutations are read in that order. A 1 denotes a listed leaf at that site and a 0 denotes absence from its list.

| Pattern | 000 | 100 | 110 | 111 | 101 | 011 |
|---|---:|---:|---:|---:|---:|---:|
| Leaves | 1 | 11 | 9 | 4 | 3 | 1 |

We also transcribed the three marker labels next to every B1 leaf icon in the original figure. The sample-table patterns match the drawing at all 16 B1 locations, comparing the leaf patterns within each location without guessing which icon denotes L1 or L2. Both presentations concern the same biological observations. [Drawn patterns by location](figure4_b1_patterns.tsv)

Each pair of marker sets has shared leaves and leaves unique to each side. The strict single-origin, irreversible model for whole-leaf binary states would allow only nested or disjoint sets. To determine the nearest pattern family consistent with that model, the calculation checks all 255 nonempty subsets of the eight possible patterns. It retains those whose three columns are nested or disjoint and minimizes the number of changes to individual binary entries. The minimum is **four of 87 entries**. Only the family {000, 100, 110, 111} attains it. This is a descriptive distance to the model. The analysis supplies no biological reason to change a particular entry. Whole-leaf DNA can contain multiple cell lineages, so these crossings leave the underlying sequence of meristem cell divisions unresolved. [Original interpretation](https://doi.org/10.1371/journal.pbio.3000191) · [Enumerated result](physical_groups.json)

## Earlier branch markers M71 and M101

The native Ji et al. Table S2 identifies M71 as Pp01:2130859 A→C and M101 as Pp04:21561355 G→A, crediting both to Wang et al. Figure 4 in the earlier paper uses its own numeric labels. Comparing how many leaves carry each marker at *each named position* uniquely links Figure marker 4 to M71 and marker 2 to M101 among the 48 S2 Data sites. The two leaf icons at position B1-1 are labelled “(2~4,15)” and “(4).” Thus both icons carry Figure marker 4 and exactly one carries marker 2. Marker 2 also occurs at other positions. All 16 location-level multisets of paired calls on B1 agree between the figure and the two matched source records. This comparison uses no assumption about which drawn leaf is L1 or L2. [Ji et al., Table S2](https://doi.org/10.1371/journal.pgen.1011829.s016) · [Wang et al., Figure 4](https://doi.org/10.1371/journal.pbio.3000191.g004) · [Drawn pair patterns](figure4_b1_patterns.tsv)

Across B1, one leaf carries both listed sites, one carries only M71, 13 carry only M101 and 14 appear on neither list. Across all 75 leaves the count on neither list is 60. This cross-check establishes that the crossing also appears in the original drawing. The diagram and the catalogue report the same study. They do not establish whether the two variants ever occupied the same cell.

Run the following command from this directory with the two source extracts. Verification uses Python’s standard library.

```sh
python3 -B physical_groups.py /path/to/carriers.tsv /path/to/sample_roster.tsv | diff - physical_groups.json
```

Figure 4 was inspected directly in the publisher’s 2,808,349-byte PDF, page 14. The PDF SHA-256 is `29d6df56c39e34c01099cbf64fb62a19a5d57b6b60e28b2cb1a04c8f75218aeb`. The embedded Figure 4 JPEG can be extracted with `pdfimages -f 14 -l 14 -j`. It has SHA-256 `ae46d850a044ddbb1b0c1a61f071e5ddb064487043b0902d997b88059b883eaf`. [Publisher PDF](https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3000191&type=printable)
