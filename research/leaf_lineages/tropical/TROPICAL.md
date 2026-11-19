# Agreement between physical and genetic branch distances in four trees

Satake et al. recorded physical branching geometry and sequenced seven branch-tip leaf samples and one basal cambium sample per tree in two individuals each of *Shorea laevis* (S1 and S2) and *S. leprosula* (F1 and F2). The authors report that physical branching topology did not enter SNV discovery. They had already observed broad agreement between neighbor-joining trees and physical architecture and some mutations inconsistent with that architecture. Their Supplementary file 1b supplies 28 paired physical and genetic distances per tree. The following calculation examines every four-sample subset directly, keeping comparisons among leaves separate from those including the basal sample. [Satake et al., 2024, Fig. 1](https://doi.org/10.7554/eLife.88456) · [Author workbook, sheet b](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx)

| Tree | Four leaf tips, agree / tie / disagree | Basal cambium and three tips, agree / tie / disagree | Exact four-point equality for SNV distances, leaf-only / with basal sample |
|---|---:|---:|---:|
| S1 | 35 / 0 / 0 | 35 / 0 / 0 | 31 / 35 and 29 / 35 |
| S2 | 35 / 0 / 0 | 35 / 0 / 0 | 35 / 35 and 35 / 35 |
| F1 | 35 / 0 / 0 | 35 / 0 / 0 | 35 / 35 and 35 / 35 |
| F2 | 29 / 6 / 0 | 24 / 6 / 5 | 35 / 35 and 35 / 35 |

All 280 physical quartets had a uniquely smallest distance sum and equal larger sums. Among 140 leaf-only quartets, the genetic distances uniquely picked the same pairing 134 times. In the remaining six, all three genetic sums were equal. In the 140 quartets that included basal cambium, 129 uniquely agreed, six were tied and five picked a different pairing. All five disagreements involved the same three samples on F2, namely the basal sample, tip 1_1 and tip 1_2. Each of the five other tips supplied the fourth member. Quartets reuse the same distances and individuals. These five observations describe one localized difference. [Reconstructed distances](tip_distances.json) · [Per-tree results and five examples](quartet_result.json)

For four labels A, B, C and D, compare the sums d(A,B)+d(C,D), d(A,C)+d(B,D) and d(A,D)+d(B,C). On a resolved additive tree with nonnegative edge lengths, the within-side pairing has the uniquely smallest sum, and the other two sums are equal. An unresolved internal edge makes all three equal. We counted the unique minimum also for nonadditive matrices, where it is a distance preference. We tested equality of the largest two sums separately. In ten S1 quartets these two genetic sums differ even though the preferred pairing matches the physical one. On F2 all genetic quartets satisfy the equality, including five that favor a different physical pairing. Thus distance additivity and agreement with independently recorded physical branching answer different questions.

For example, take F2 samples A=basal cambium, B=1_1, C=1_2 and D=2_1. The physical sums are 54.40, 54.40 and 52.20 metres, which favor AD|BC. The genetic sums are 38, 42 and 42 differences, which favor AB|CD. The basal sample represents a tissue collected at the base of the stem. Its recorded state does not establish the genotype of the tree’s founder. Genetic distance aggregates many mutation differences and the quartet has no arrow of time. Individual mutation order, separate origins, and the reason for the local discordance remain unresolved. The calculation concerns four trees in one study, with two trees per species.

A 2026 preprint by Tomimoto and colleagues reuses the Satake observations and models stem-cell dynamics. Its analyses of non-nested site patterns and physical-versus-genetic topology provide relevant prior work. Those results and this quartet check use the same four biological individuals. [Preprint and data statement](https://doi.org/10.64898/2026.04.02.716038)

## Reproduce

Run from this directory. The archived JSON records the verified SHA-256 and gives distances in centimetres and mutation differences. The offline calculation and its verifier use the Python 3 standard library. Native XLSX extraction requires openpyxl, and the independent workbook verification reads the original XML directly.

```sh
python3 -B quartet.py | diff - quartet_result.json
python3 -B verify_quartets.py
python3 -B quartet.py --extract /path/to/elife-88456-supp1-v1.xlsx | diff - tip_distances.json
python3 -B verify_quartets.py --workbook /path/to/elife-88456-supp1-v1.xlsx
```
