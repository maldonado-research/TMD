# Separate founding assay in the standard diploid wells

In a separate proof-of-concept experiment, Fasanello et al. measured 91 diploid yeast strains against a common reference in ten replicate pools. The ten-repeat measurement called the day-25 leader in **18 of 21** standard diploid wells. Adding the observed day-0 ratio gave **16 of 21**, compared with **11 of 21** for the day-0 leader. The combined forecast corrected six baseline calls and lost one. Its mean absolute error was 0.26035 in final share, compared with 0.27679 for the baseline share. The predicted direction of share change was correct in **11 of 21**. [Source study](https://doi.org/10.7717/peerj.10118)

The matched four-repeat generation-zero assay called 10 leaders, 12 combined winners and 11 gain directions in these same 21 wells. Its combined share error averaged 0.38630. The two assays agreed on the faster founder in only 9 wells. Their shared stock identifiers support strain matching across the experiments. The original 91-label assay used fresh samples from the source strain stocks, a different-sized pool, and a different sequencing library. Each of its replicates supplied one shared measurement across all 16 compared pairs. Eleven founder pairs occur once among the 21 wells and five occur twice. These experiments supply separate fitness measurements for the same evolved populations. The study selected the barcodes with the expectation of equal fitness. [Experimental design](https://doi.org/10.7717/peerj.10118)

The separate-assay rule was committed at `a6640f2` after scoring the main assay and before joining the proof-of-concept measurements to outcomes. The exploratory checks in `proof_results.json` give a mean assay-only accuracy of 7/8 with equal weight for each of the 16 pairs. Choosing each of the ten repeat pools alone gives 11–18 of 21 correct, and omitting each repeat in turn gives 14–19. The combined share error was smaller than baseline in 9 of 21 wells. These checks describe the observed roster and measurement variation.

## Offline replay

From this directory, run the following command with Python 3.9 or newer.

```sh
python verify_proof.py
```

The script reads `proof_pairs.tsv` and `proof_wells.tsv`. The first contains four focal counts and the two common reference counts for each of 16 pairs in each of the ten repeat pools. The second contains the 21 well memberships, starting and ending longitudinal counts, and the exact product of the four generation-zero pair rate ratios. The A label is the lexicographically first normalized label in each pair. IDs Q001–Q016 follow sorted normalized pairs in this subset. The population IDs follow the native evolution table order used in TMD 0.11.0. [Earlier roster](https://doi.org/10.5281/zenodo.24382132)

For each repeat, divide the founder's final-to-initial count ratio by the corresponding reference ratio. Divide that result for A by the result for B to obtain one relative growth ratio. The shared measured reference cancels in all pairs. With product P over the ten repeats, the mean per-generation log fitness contrast is log(P)/200. The ten repeats each measure 20 generations. If O is the starting A:B odds, the projected odds at 250 generations are O times P raised to 250/200. The verifier uses integer and rational arithmetic for all ranks. Assay counts include the authors' pseudocount of one. Longitudinal counts reverse that adjustment to match the TMD panel. The benchmark has zero unresolved forecasts and zero endpoint ties.

## Native-source replay

The extract uses the Fasanello repository at commit `a370be7497fda328c6c8b13d957223ff4cba53c6`. Library 001 contains the separate proof-of-concept assay, and library 002 contains the four-repeat founder assay and evolution data. In library 001 metadata, samples 1–10 are initial observations and 51–60 are the corresponding final observations. The extraction checks all 3,640 archived focal and reference counts against the original matrix plus one, along with the 910 published per-repeat fitness values. Thirty-two focal stock labels match the standard diploid condition. The native library-002 suffix B is removed for duplicated labels in set S14 for this subset, as documented in the source. [Archive](https://doi.org/10.5281/zenodo.3888967) · [Library 001 preparation](https://github.com/VinceFasanello/MM_Code_Supplement/blob/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/001_Prepare_Datasets/001_Prepare_Datasets.Rmd) · [Library 002 preparation](https://github.com/VinceFasanello/MM_Code_Supplement/blob/a370be7497fda328c6c8b13d957223ff4cba53c6/2_CountstoAnalysis/002_Prepare_Datasets/002_Prepare_Datasets.Rmd)

| Input under `2_CountstoAnalysis/` | SHA-256 |
| --- | --- |
| `001_Prepare_Datasets/poc92.Rdata` | `90b43ee601d269ccc8d03344ae92d6692c74723af609b55353508029333574da` |
| `001_Raw_Data_Metadata/001_counts.expected.Rdata` | `c6186f5710f24a8d2081f70dda299bf97a10cef6849ebc84f9d6f7850e59c3c3` |
| `001_Raw_Data_Metadata/001_Metadata.csv` | `7678ddbd1bb47f89510844de6efc6a793db4e31678c4afcac5a84306e691e335` |
| `002_Prepare_Datasets/myfa.Rdata` | `f20f592d570614b0add41d1181900570e75338f73bffdae95100e98001e03f3d` |
| `002_Prepare_Datasets/myevo.Rdata` | `f10be28895efc07a2106f8de08e38661ccc75139826e919ffe54b170aa41d9e0` |

The native scripts require the Python `rdata`, `pandas` and `xarray` packages. The following example assumes the five input files are in the current directory. Each argument also accepts an explicit path. The optional export writes the two anonymous TSVs to the specified directory.

```sh
python proof_assay.py poc92.Rdata 001_counts.expected.Rdata 001_Metadata.csv myfa.Rdata myevo.Rdata --export regenerated
python verify_proof.py --directory regenerated
python verify_native_fitness.py myfa.Rdata myevo.Rdata
```

`proof_native_receipt.json` records the proof-assay extraction checks and native forecast scores. `native_fitness_receipt.json` records the independent native replay of the main 76-well experiment. It joins the two native R tables using source treatment and both exact assigned labels. It verifies the reference counts and reciprocal pair orientation for each of the four founder repeats. Only generation-zero measurements enter its fitness estimates.
