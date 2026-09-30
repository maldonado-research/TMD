# An authenticated secondary-data starting point for TMD

This folder contains a manual transcription of the 96 numeric body cells of Leehan and Nicholson's 2021 Table 1, plus a reproducible, exploratory analysis. The primary [ASM article, DOI 10.1128/AEM.01237-21](https://journals.asm.org/doi/10.1128/aem.01237-21) is the source of the observations. Ricardo's project did not collect these observations.

The table separates three experimental blocks and two media. The study sampled one resistant colony from each eligible culture. These are endpoint sampled genotypes, with no measured first-arrival time. The CSV is an attributed secondary transcription, not the authors' original culture-level instrument file. See [RPOB_SOURCE_PROVENANCE.md](RPOB_SOURCE_PROVENANCE.md) for cell mapping and eligibility.

## Results

| Sample definition | LB | SMMAsn | Pooled context–route MI, bits | Held-out log-score improvement over pooled, bits | Improvement per observation, bits |
|---|---:|---:|---:|---:|---:|
| All sequenced resistant isolates, 16 classes | 59 | 52 | 0.260835 | 13.125729 | 0.118250 |
| Identified point substitutions, 14 classes | 53 | 51 | 0.251382 | 12.700734 | 0.122122 |

The often-repeated 59/52 versus 53/51 denominator discrepancy is explained by the sample definition: the latter excludes six isolates with no identified mutation and one insertion categorized as Other. The existing TMD count file matches all 32 aggregate Table 1 cells after the source label `No mutation found` is mapped to `NoMutationFound`.

We fitted two models on two experimental blocks and scored the third, repeating for all three blocks. The pooled model ignores medium. The context model fits one route distribution per medium. Both use a Dirichlet pseudocount of 0.5 per route. The context model predicts each held-out block better under either sample definition. This is a descriptive demonstration that context contains useful predictive information in this published dataset.

## What this establishes

The new contribution here is the source reconciliation, restoration of experimental blocks, and reproducible secondary prediction analysis. Environment-associated spectra were already a result of the original paper. Our calculations do not establish a new causal mechanism, confirm TMD's μ/A/F decomposition, measure biological arrival hazards, or test the gamma-race timing module. They provide a better-grounded empirical testbed for those later questions.

This analysis was planned after viewing these data. It is exploratory. No p-values or confidence intervals are offered because treatment randomization, culture-level records, and the full sampling process have not been independently verified. Positive plug-in MI is expected even under noise, especially with small sparse tables. The block-conditional MI in `rpob_results.json` is descriptive; its larger value should not be interpreted as a significance gain.

## Reproduce

Run from any working directory with Python 3:

```text
python analyze_rpob.py
```

The script reads the CSV beside it and writes `rpob_results.json` there. It uses only the standard library. It verifies 96 unique nonnegative cells and the primary published totals. It implements:

\[
I(C;R)=\sum_{c,r}\frac{n_{cr}}{N}\log_2\frac{n_{cr}N}{n_c n_r},
\]

and for a held-out block,

\[
\Delta L=\sum_{c,r}n^{\rm test}_{cr}\log_2\left[
\frac{(n^{\rm train}_{cr}+1/2)/(n^{\rm train}_{c}+K/2)}
{(n^{\rm train}_{r}+1/2)/(N^{\rm train}+K/2)}
\right].
\]

The held-out outcomes never enter training in their own fold. Reusing folds and choosing this analysis after seeing the published results prevents treating it as a prospective TMD prediction.

## Data attribution and rights

The CSV contains factual numerical observations transcribed from the cited table; no article prose or figure is reproduced. The publication states copyright © 2021 American Society for Microbiology, all rights reserved. This folder does not apply a new license to that publication, its figures, or any unprovided culture-level data. Preserve the source citation if sharing the transcription. The analysis code and new explanation must receive any project license separately from source materials.
