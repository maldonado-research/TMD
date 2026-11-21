# Which sampled branches can carry a change of genotype?

Satake et al. sequenced leaves at seven branch tips and cambium at the base of each of four tropical trees. They measured the physical branching distances independently of variant discovery. An earlier TMD report compared physical and genetic distances for these same trees. Here we return to the original **1,136 site-by-sample records** and ask which genotype changes fit one anatomical branch and which pairs have a forced order under that interpretation. This is a retrospective analysis of the same four individuals. [Satake et al.](https://doi.org/10.7554/eLife.88456) · [Original workbook, sheets b, f and k](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx) · [Earlier TMD distance analysis](https://github.com/maldonado-research/TMD/tree/6fa3871b25eb4896edfad8cb38f6bb7d306108c4/research/leaf_lineages/tropical)

## A cross-sheet discrepancy

The individual prefixes in the genotype worksheet k differ from those in the distance worksheet b, count worksheet f and published figure. A naive join by the printed F/S identifier assigns sites to the wrong individual. We reconstructed all 28 pairwise genetic distances per genotype block by counting sites where two samples had different diploid genotypes. Comparing each block with **all four** distance matrices gives a unique exact match. All 112 pairwise entries match under the corrected crosswalk. Each total also matches the final site count in worksheet f. The species labels on worksheet k agree with the recovered identities. The independent verifier checks the workbook XML. [Native workbook](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx) · [Crosswalk and compact data](satake_patterns.json)

| Genotype block in k | Identity in b and f | Source sites | Two observed genotypes | Three observed genotypes | Two-state sites fitting one physical edge |
|---|---|---:|---:|---:|---:|
| S. laevis: F1 | S1 | 728 | 711 | 17 | 706 |
| S. laevis: F2 | S2 | 234 | 234 | 0 | 234 |
| S. leprosula: S1 | F1 | 106 | 105 | 1 | 105 |
| S. leprosula: S2 | F2 | 68 | 68 | 0 | 66 |

Raw genotype calls are 0/0, 0/1 and 1/1. These categorical differences in bulk samples can reflect allele balance, mosaicism or changes in genotype. Across the complete 1,136 sites, the minimum number of genotype transitions on the sampled anatomical tree was **one at 1,111 sites and two at 25 sites**, using unit cost between any two different genotype calls. The 25 include seven two-state patterns that cross branches and all 18 three-state patterns. These are parsimony scores for the recorded characters. They give no direct counts of de novo mutations. [Per-tree results](satake_placements.json)

## What one missed departure can change

For the timing interpretation, restrict to the 1,118 sites with exactly two observed genotypes. Orient each binary character relative to the *sampled* basal genotype. A tip is positive when its genotype differs from that basal reading. As a diagnostic model, place one stable genotype transition on a branch of the base-rooted physical tree, assume all sampled descendants inherit it, and treat positive calls as correct. The orientation is a convention. The basal sample is contemporary cambium, and the paper sequenced bulk tissue. The genotype of the ancestral cell and its division tree are unknown. [Collection and genotyping](https://doi.org/10.7554/eLife.88456)

Write P for the positive tips, N for secure negative tips and D(e) for the sampled tips descended from edge e. A transition on e is compatible exactly when P is contained in D(e) and D(e) contains no member of N. Unmeasured tips impose no constraint. To allow at most b reported basal-state tips per site to conceal a departure, replace the second condition by |D(e) ∩ N| ≤ b. This is an assumed error budget for sensitivity analysis. With an observed positive, all edges containing P lie along the path from the base to the positive tips’ most recent common ancestor. As one moves towards that ancestor, the number of included negative tips can only decrease. The compatible edges therefore form a contiguous segment whenever any qualify. Necessity follows from inheritance. Sufficiency follows by placing the transition on the candidate edge and assigning the allowed missed departures to the negative descendants. Each edge in the returned segment has such a witness.

For these complete seven-tip call patterns, the minimum budget equals the number of basal-state tips below the positive tips’ common ancestor. The seven incompatible two-state sites each need exactly one missed departure to fit this model. The same allowance expands the possible placements of other sites. At budget one, **622 of 1,118 sites have two compatible edges** and 496 have one. At budget zero, 1,111 had exactly one candidate and seven had none. Alternative explanations include cellular mosaicism, differences between physical and cell-lineage trees, or multiple genotype transitions. The calculation estimates none of their probabilities.

For a pair of compatible sites, precedence along the same lineage is forced only if every permitted edge for one is a strict ancestor of every permitted edge for the other. Two transitions on the same edge have no forced internal order. Transitions on separate branches also have no forced calendar order without dates. These statements allow transitions anywhere in edge interiors and independent per-site budgets. The published branch lengths are measured in metres. They cannot supply elapsed years or cell-division times.

| Within-tree site pairs | Exact calls | Up to one missed departure per site |
|---|---:|---:|
| Forced precedence by strict ancestry | 72,219 | 59,736 |
| Always on separate branches | 177,936 | 161,625 |
| Both restricted to the same edge | 33,576 | 10,392 |
| Several possible relative placements | 0 | 55,651 |
| At least one site incompatible | 3,673 | 0 |
| Total | 287,404 | 287,404 |

Holding membership fixed at the **1,111 sites that fit with exact calls**, the number of forced pair orders drops from **72,219 to 56,745** when one missed departure is permitted. Newly compatible sites account for the other 2,991 ordered pairs in the all-site one-miss column. The sums combine within-individual pairs. They exclude every cross-tree comparison. These pairs share sites and individuals, and the larger S1 block contributes most of them. They measure what the observation design can distinguish. Origin time, clonal establishment and the number of lost mutations require further evidence. [Output by tree and budget](satake_placements.json)

Single-change perfect phylogeny, reconstruction from tree distances and genotype parsimony are established methods. The contribution here is the cross-sheet identity check and the explicit sensitivity of this dataset’s relative order to a specified missed call. A 2026 preprint by Tomimoto and colleagues models stem-cell dynamics and topology discordance in these same trees. It uses the same biological observations. [Perfect phylogeny](https://doi.org/10.1002/net.3230210104) · [Character parsimony](https://doi.org/10.2307/2412116) · [Tomimoto et al.](https://doi.org/10.64898/2026.04.02.716038)

## Replay

The compact JSON retains pattern counts, pairwise physical distances, and the label matching for every tree. In its state patterns, 0 represents the base’s called genotype and subsequent states are numbered in order of first appearance. No genome coordinates or sequences are necessary. Distances are in centimetres. Each list follows lexicographic pairs of *indices* in the supplied sample order. These observed cells and their original publication are credited to Satake et al. [Native workbook](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx)

Use Python 3.11 or later. The first two commands work offline. Optional native extraction uses openpyxl. The last command independently reads the original workbook with the Python standard library. The independent checker reconstructs physical splits by testing every subset against all separating quartets, enumerates alternative tip calls and assigns internal genotypes exhaustively. The primary implementation uses shared path lengths, descendant sets and dynamic programming.

```sh
python3 -B satake_branches.py | diff - satake_placements.json
python3 -B verify_satake.py
python3 -B satake_branches.py --extract elife-88456-supp1-v1.xlsx | diff - satake_patterns.json
python3 -B verify_satake.py --workbook elife-88456-supp1-v1.xlsx
```

The workbook SHA-256 is `a5916e95facc077a137ce03627b2a94ef7ecf3cc9a148223587bdb719d2a06af`.

The archive includes an unchanged copy of Supplementary file 1 from Satake and colleagues. The article and its supporting material are distributed under Creative Commons Attribution 4.0. In the native-source commands above the filename refers to that included workbook. A second analysis places a limit on missed calls across the entire panel and counts which pair identities retain their order across all reconstructions. [Original authors and supplement](https://doi.org/10.7554/eLife.88456) · [License](https://creativecommons.org/licenses/by/4.0/) · [Whole-panel results](panel_budget/README.md)
