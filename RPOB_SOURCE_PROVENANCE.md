# Source-to-cell provenance

- Authors: Joss D. Leehan and Wayne L. Nicholson.
- Year: 2021.
- DOI: [10.1128/AEM.01237-21](https://doi.org/10.1128/AEM.01237-21).
- Primary table read: [ASM Table 1](https://journals.asm.org/doi/10.1128/aem.01237-21).
- Read and transcribed: September 30, 2026.
- Method: manual transcription of published numeric table cells; no inferred missing values, fabricated isolate identifiers, or synthetic times.
- File: `leehan2021_table1_by_block.csv`, 96 observations of table cells, representing 111 sampled isolates after summing counts.

## Exact mapping

Each CSV row maps to one body cell as follows:

| CSV field | Primary table location |
|---|---|
| source_doi | Article DOI |
| source_table | Table number 1 |
| source_row | Exact mutation/label row: S465P through Other |
| experimental_block | First, second, or third published replicate group |
| context | LB or SMMAsn subcolumn of that replicate group |
| count | Integer in that body cell |

The first six numeric body columns, in reading order, are block1/LB, block1/SMMAsn, block2/LB, block2/SMMAsn, block3/LB, block3/SMMAsn. The last two total columns are validation targets and are not transcribed as additional observations. There are 16 row categories × 3 blocks × 2 contexts = 96 cells. A zero is a published zero, not an imputed missing value.

## Validated table totals

| Block | LB | SMMAsn | Total |
|---|---:|---:|---:|
| 1 | 19 | 19 | 38 |
| 2 | 20 | 19 | 39 |
| 3 | 20 | 14 | 34 |
| All | 59 | 52 | 111 |

`No mutation found` contributes (1,1), (2,0), (2,0) across the three blocks; `Other` contributes (1,0), (0,0), (0,0). Excluding these rows yields point-substitution totals 53 and 51. The source describes Other as a +3 bp insertion. These eligibility decisions are separate from the source's growth/fluctuation-assay exclusions.

The Table 1 totals exceed the number of identified point mutations; the prose's smaller denominators should therefore not be treated as an arithmetic failure of the table. The choice of all sampled resistant isolates or identified point substitutions changes the estimand and must be stated.

## Authentication boundary

This is published aggregate observational evidence with table-level lineage. It is not original raw sequencing output, culture-by-culture counts, endpoint plating records, or independently audited lab notebooks. We have verified agreement with the published table and the project's existing aggregate file, but not independently reidentified mutations from chromatograms. The paper's methods support distinct cultures and three experimental blocks; this audit has not established random treatment assignment or statistical exchangeability. No first-winner event or physical time is contained in this transcription.
