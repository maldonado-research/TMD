# A missing upstream marker in a lysate that still records its downstream markers

Ji et al. place M101 in the main branch, M119 in its sub-branch and M21 in Flower #2. Their Figure 3 interprets these as nested markers of the same Group 1 cell lineage. One Flower #2 stamen sample, Pair19, had M101 alternate counts of **0 of 248** and **43 of 215** in its two separately sequenced lysate aliquots. The zero-count aliquot still recorded M119, M21 and two Group 2 markers. Both libraries covered 91.8% of the genome with at least five reads. These observations establish that alternate-marker signal was recoverable in that aliquot. They leave unresolved why the M101 allele was absent from its reported reads. [Primary study, Figure 3 and Methods](https://doi.org/10.1371/journal.pgen.1011829) · [S1 mapping statistics](https://doi.org/10.1371/journal.pgen.1011829.s015) · [S7 read counts](https://doi.org/10.1371/journal.pgen.1011829.s021)

| Measurement | Aliquot A, T8710-X4-2a | Aliquot B, T8710-X4-2b |
|---|---:|---:|
| Mean mapped depth, mapping quality ≥20 | 49.27 | 51.08 |
| Genome covered by ≥5 reads | 91.8% | 91.8% |
| M101, Group 1, alternate / total | 0 / 248 | 43 / 215 |
| M119, Group 1, alternate / total | 6 / 26 | 10 / 47 |
| M21, Group 1, alternate / total | 3 / 36 | 2 / 44 |
| M71, Group 2, alternate / total | 32 / 71 | 9 / 68 |
| M42, Group 2, alternate / total | 16 / 89 | 42 / 107 |

The original library inventory, the Flower #2 count table and the split-sample roster assign both aliquots to stamen unit 4. The cell-variant-frequency supplement reprints all five pairs of marker counts for these libraries. Across the 40 split aliquots S7 and S8 match at all 200 checked sample–marker combinations. The native Flower #2 workbook also agrees with the overlapping M21 and M42 counts in all 80 cases. S8 derives its cell-frequency estimates from the same readouts. S11 examines seven progeny. Neither supplies an independent true genotype for the M101 observation in this lysate. The inspected tables contain mapping summaries and selected marker panels. They provide no independently measured genome-wide rate of allele loss for these two aliquots. [S3 tissue counts](https://doi.org/10.1371/journal.pgen.1011829.s017) · [S5 pair roster](https://doi.org/10.1371/journal.pgen.1011829.s019) · [S8 frequency calculations](https://doi.org/10.1371/journal.pgen.1011829.s022) · [S11 progeny](https://doi.org/10.1371/journal.pgen.1011829.s025)

## Two departures from read-level nesting disappear under pooling

Represent observed M101, M119 and M21 by three bits in that order. A one means at least one alternate read. Among 40 aliquots, the patterns were 111 in 35, 110 in three, 001 in Pair1b and 011 in Pair19a. If observed labels had to be perfectly nested, the only allowed patterns would be 000, 100, 110 and 111. The minimum change would be two sample–marker labels, one in each exceptional aliquot. If all positive labels were preserved, three additions would be necessary and sufficient. If all zero labels were preserved, three deletions would be necessary and sufficient. These minima follow from enumerating the four allowed patterns in each row. They count edits under the stated observation rule. They cannot identify erroneous measurements, a mutation-loss rate or the order of events on their own. The paper’s lineage assignments used additional evidence, including branch position and frequency correlations.

Combining each pair’s counts before assigning the bits gives 111 in all 20 lysates. Pooling thus obscures both read-level exceptions. The finite roster contains one flower, and the same tissue and markers contribute repeated observations. No independent probability of recovering a genuinely present allele was estimated. [Source-derived input](aliquot_profiles.csv) · [Counts and exact edit minima](aliquot_result.json)

## Reproduction

Run from this directory. The default command uses only Python 3.10 or later. The optional source extraction also uses openpyxl. S1, S3 and S5 were replayed from pinned XLSX files. S7 and S8 were read from publisher-linked workbook renderings. The extractor accepts either the native S7/S8 workbooks or Markdown table renderings which preserve their headers and records. The supplied CSV is a reduced join of those sources. The counting rule and minimum-edit calculation are original to this analysis.

```sh
python3 -B aliquot_controls.py | diff - aliquot_result.json
python3 -B aliquot_controls.py --extract S1.xlsx S3.xlsx S5.xlsx S7.xlsx S8.xlsx | diff - aliquot_profiles.csv
```
