# Fasanello yeast lineage counts

Fasanello et al. (2020) followed two labelled baker’s yeast lineages in each of 76 wells. The authors sampled the initial mixture on day 0 and followed the same wells on days 10, 15, 20, 22, 24 and 25. They intended to mix equal proportions. An observed day-0 read-count leader therefore answers a question about measured baseline abundance. The design supplies no deliberate initial numerical advantage. Starting mixtures, sampling and assay effects can each contribute to the difference between the intended and measured proportions. Each well and day has one retained measurement. [Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7571412/)

The final day corresponds to approximately 250 generations under the standard transfer treatment. The authors estimate approximately 200 and 300 generations for conditions 5 and 6, respectively. Calendar days provide the common time axis. The endpoint tracks the combined descendants carrying each original label, including descendants that subsequently change. The counts estimate relative abundance within the assigned pair. [Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7571412/)

## Native source

The 56,792-byte file `myevo.Rdata` contains the authors’ processed R data frame with 76 rows and 140 columns. Its SHA-256 digest is `f10be28895efc07a2106f8de08e38661ccc75139826e919ffe54b170aa41d9e0`. Commit `a370be7497fda328c6c8b13d957223ff4cba53c6` pins the source. [Native file](https://raw.githubusercontent.com/VinceFasanello/MM_Code_Supplement/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/002_Prepare_Datasets/myevo.Rdata) · [Archived release](https://doi.org/10.5281/zenodo.3888967) · [Preparation script](https://github.com/VinceFasanello/MM_Code_Supplement/blob/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/002_Prepare_Datasets/002_Prepare_Datasets.Rmd)

The authors add one pseudocount to each expected barcode count and, when a sample was resequenced, keep the run with the lower estimated contamination. Their analysis table retains the two-barcode experimental wells and removes a reference pair. The extraction subtracts one from each of the two assigned counts for each well/day. Symmetric subtraction preserves the rank and changes reported read fractions slightly. There are 532 rows, each with a positive combined count. The native `p0` through `p25` columns agree with the native counts before pseudocount subtraction. [Count preparation](https://github.com/VinceFasanello/MM_Code_Supplement/blob/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/002_Prepare_Datasets/002_Prepare_Datasets.Rmd#L72-L99) · [Fraction computation](https://github.com/VinceFasanello/MM_Code_Supplement/blob/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/002_Prepare_Datasets/002_Prepare_Datasets.Rmd#L750-L763)

## Export fields

| Column | Meaning |
| --- | --- |
| `population_id` | Distinct experimental well, W001–W076, in native table row order. |
| `pair_id` | The 44 distinct exact pairs of native short labels, including list suffixes added by the authors. |
| `label_pair_id` | The 38 distinct pairs of normalized underlying labels. Pools matching labels across ploidies. |
| `strain_pair_id` | The 44 distinct combinations of ploidy and normalized label pair. Keeps haploid and diploid backgrounds separate. |
| `condition_id` | Study treatment. Codes 1–6 appear below. |
| `day` | Elapsed calendar day. |
| `reads_A`, `reads_B` | Counts assigned to each partner after subtracting one native pseudocount per barcode. A is the lexicographically first normalized short label of the pair at every time and in every condition. |

The authors added a trailing B to specific duplicate short labels in sets S14 and S2. The extractor reverses those two documented transformations. It assigns pair IDs in lexicographic key order. The two groupings with 44 distinct pairs have different memberships. Matching short labels across ploidies establish a shared barcode identifier, while ploidy distinguishes biological backgrounds. [Duplicate labels](https://github.com/VinceFasanello/MM_Code_Supplement/blob/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/002_Prepare_Datasets/002_Prepare_Datasets.Rmd#L643-L658)

| Condition | Native treatment | Wells |
| --- | --- | ---: |
| 1 | CMdiploid0.001 | 21 |
| 2 | CMhaploid0.001 | 11 |
| 3 | CM+Ethanoldiploid0.001 | 11 |
| 4 | CM+Saltdiploid0.001 | 11 |
| 5 | CMdiploid0.004 | 11 |
| 6 | CMdiploid0.00025 | 11 |

## Reproduction

With Python, pandas and pyreadr installed, run `python read_fasanello.py myevo.Rdata fasanello_counts.tsv`. The extraction checks the pinned native source digest, pair definitions, positive totals and agreement with the native frequencies. The output SHA-256 digest is `80845b53a4b82ffa739fd337e712a15269e56220be255b399fdffdf0b5d46ae9`.
