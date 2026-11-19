# Shared misses depend on where a detection assumption is applied

Ji et al.'s two splits give 50 double-positive, nine A-only, 12 B-only and 669 double-reference comparisons. Suppose each of these 740 tissue–site comparisons has one binary biological state and every positive call is genuine. Then **every hidden count from 0 to 669 is possible**. Assign any chosen subset of the double-reference comparisons to be truly positive. The 37 sites were already ascertained through wider screening of one peach flower. This analysis only addresses the site–tissue grid in that flower. [Ji et al.](https://doi.org/10.1371/journal.pgen.1011829)

For a group with I double positives, A and B single positives, and Z double-reference comparisons, let h be the number of hidden positives among the Z. As an explicit extra assumption, impose $Ih \leq \Gamma AB$, with a nonnegative finite multiplier Γ. Where all four cells among true positives are positive, this caps the realized detection odds ratio. Writing the cross product specifies how the restriction handles zeros. When I > 0 the allowable integers run from zero to min(Z, floor(ΓAB/I)). When I = 0 they run from zero to Z. Every such integer is attainable, and independent choices of assignments in disjoint groups attain every integer from zero through the sum of their ceilings.

| Apply the cap to | Hidden count at Γ = 1 | At Γ = 2 | At Γ = 10 | Minimum recovery by either split at Γ = 1 |
|---|---:|---:|---:|---:|
| All 740 comparisons together | 0–2 | 0–4 | 0–21 | 71/73 |
| Each of the 20 tissues | 0–3 | 0–6 | 0–30 | 71/74 |
| Each of the 37 sites | 0–510 | 0–512 | 0–524 | 71/581 |

Pooling gives an upper endpoint of min(669, floor(54Γ/25)). Every tissue has a double-positive call. Only two tissues have both kinds of single-positive calls, giving the tissue ceiling min(33, floor(2Γ)) + min(32, floor(Γ)). In contrast, the 26 sites without a double positive contain **508** double-reference cells. All 508 can be hidden positives under any one-sided site cap. One further site has I = 1, A = 2, B = 1 and Z = 16, allowing two additional misses at Γ = 1. The remaining sites contribute zero, giving the general site ceiling 508 + min(16, floor(2Γ)). For any allowed h, the true-positive denominator is 71+h, A misses 12+h, B misses 9+h, and both miss h.

These restrictions apply to different tables. A cap in one grouping gives no general guarantee that the same cap holds in another. With a zero product AB and positive I, any finite cap forces h = 0 in that group, however large Γ becomes. Lifting the restriction entirely permits all 669 double-reference comparisons in every grouping.

The data supply no calibration for Γ. Under stochastic independence, observed cross products can differ by chance. Requiring exact equality here would demand 50h = 108 for the pooled counts, which has no integer solution. The calculations are finite assignments conditional on the stated truth and dependence assumptions. Link discusses heterogeneous detection and nonidentifiability. Sun et al. develop statistical confidence intervals based on bounds on population capture odds ratios. [Link](https://doi.org/10.1111/j.0006-341X.2003.00129.x) · [Sun et al.](https://doi.org/10.1093/jssam/smac031)

Run these commands from the directory containing this note. The count calculation and independent enumerator use the Python standard library. Replaying Tables S2 and S5 also uses openpyxl. The receipt lists the input URLs and SHA-256 values.

```sh
python3 -B shared_miss_bounds.py | diff - shared_miss_result.json
python3 -B verify_shared_miss.py
python3 -B replay_site_calls.py /path/to/pgen.1011829.s016.xlsx /path/to/pgen.1011829.s019.xlsx | diff - site_calls.json
```
