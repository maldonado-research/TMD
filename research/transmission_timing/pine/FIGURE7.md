# A linked pine marker predicts different outcomes within the same genotype

Guner et al. measured dwarfism in offspring from cone-bearing loblolly pine brooms and three related Nana mothers. Their Figure 7 groups the offspring by the diploid genotype at marker PitaSNP205637. Red and gray points denote dwarf and normal seedlings. The authors placed this marker in a region associated with dwarfism on linkage group 8. The following counts come directly from the 571 colored circles in the author-deposited vector PDF. The graph contains one panel each for WB-10 and WB-20 and one pooled panel for the three Nana half-sib mothers. Each count here describes a displayed point. [Published figure and caption](https://www.nature.com/articles/s41437-025-00814-5/figures/7) · [Author PDF at the verified commit](https://github.com/pgnrnr/dwarfism/blob/5d3e28d59955ae5c40e9988c80d399cb9018fd11/Figure%207.pdf)

| Family panel | A/A, dwarf / displayed | A/G, dwarf / displayed | G/G, dwarf / displayed | All displayed |
|---|---:|---:|---:|---:|
| WB-10 | 2 / 46 | 53 / 70 | 18 / 18 | 134 |
| WB-20 | 3 / 40 | 41 / 63 | 14 / 14 | 117 |
| Nana, pooled | 8 / 69 | 120 / 188 | 54 / 63 | 320 |
| All | 13 / 155 | 214 / 321 | 86 / 95 | 571 |

The G/G genotype was associated with dwarf stature in 32 of 32 displayed offspring of the two field families and 54 of 63 in the Nana panel. Treating each marker genotype as specifying one phenotype unavoidably disagrees with some displayed outcomes. If a genotype occurs with D dwarf and N normal outcomes, any deterministic assignment to it must disagree with at least min(D,N) outcomes. Selecting the more common phenotype attains that bound. Across the three genotypes the minimum is **13 + 107 + 9 = 129 disagreements in 571 displayed points**. Of the eight possible binary rules, only assigning A/A to normal and the two G-bearing genotypes to dwarf attains that minimum. The panel-wise minima are 19 for WB-10, 25 for WB-20 and 85 for Nana. The same predictions attain each minimum, so allowing a separate rule for each of those panels gives the same 129 disagreements. The experiment supplies no individual Nana-mother labels in Figure 7 that would support finer conditioning from this plot.

These counts describe an association at a marker selected from a genome-wide analysis. The calculation is a finite in-sample lower bound on disagreement. Its units are offspring observations within maternal families, participants in the discovery analysis. Those points are neither independent mutation origins nor a prospective predictive trial. Possible contributors to discordance include linkage to an unobserved causal variant, segregation, heterogeneous genetic backgrounds, incomplete penetrance and phenotyping. The data inspected do not distinguish these explanations or identify the causal molecular change.

## What differs among the published records

The paper states that 55 of 64 minor homozygotes in Nana were dwarf. The deposited PDF shows 54 of 63. The paper gives 14 of 156 major homozygotes as dwarf overall, while the PDF shows 13 of 155. The normal counts implied by these two prose margins match the respective normal counts in the figure. One extra dwarf observation in each indicated genotype would reconcile those particular margins. The source provides no basis for adding either point or selecting a single authoritative individual roster from that comparison. Both sources support a high dwarf fraction among minor homozygotes and exceptions in Nana. In WB-10 alone, the figure contains 134 points, Table 1 lists 120 alongside the genotyping platform, and the Results give 78 dwarf plus 67 normal phenotyped seedlings. No named identifiers link those three rosters. [Study Results](https://doi.org/10.1038/s41437-025-00814-5) · [Table 1](https://www.nature.com/articles/s41437-025-00814-5/tables/1)

The authors' main GitHub branch at commit 5d3e28d59955ae5c40e9988c80d399cb9018fd11 contains a README and six figure PDFs. The earlier files named data and scripts in that branch's public history each contain a single newline. The Figure 7 PDF has no embedded data file. Its SHA-256 is ade8ac17497ac11a3b8cf6392099a732475fde846cca5659ccb226f152fddd79. The extraction uses the PDF text labels to locate each family and genotype and counts each curve-defined circular point once, even when points overlap visually. All point outlines lie within their panel bounds. The distinct fill colors reproduce the figure caption's outcome key. [Original files](https://github.com/pgnrnr/dwarfism/tree/5d3e28d59955ae5c40e9988c80d399cb9018fd11) · [Reduced counts](figure7_counts.tsv)

From this directory, the first command uses only the Python standard library. The second reads the original PDF and requires PyMuPDF.

```sh
python3 -B figure7_counts.py | diff - figure7_results.json
python3 -B figure7_counts.py --extract 'Figure 7.pdf' | diff - figure7_counts.tsv
```
