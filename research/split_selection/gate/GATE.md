# How the five-read screen changes the peach benchmark

Ji et al. screened candidate sites across samples. We interpret the Methods’ inclusive five-read description as a per-sample alternate-support screen. Table S13 uses a strict threshold, and the published pipeline has additional filters. [Comparison of the original descriptions](../source/ASSESSMENT.md) For Flower #2 the published counts let us apply a version of this condition to the 40 split libraries and 30 other flower libraries at the 37 already discovered sites. Conditioning on passing this single count screen raises the expected number of one-sided comparisons from **3.18 to 7.13**, against **14 observed** among 64 comparisons with at least two pooled alternate reads. [Primary study, Methods](https://doi.org/10.1371/journal.pgen.1011829) · [Table S3](https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s017.xlsx)

| Five-read screen on the observed margins | Sites | Scored comparisons | One-sided observations | Expected before conditioning | Expected after conditioning |
|---|---:|---:|---:|---:|---:|
| At least one of the other 30 flower libraries already passes | 26 | 50 | 5 | 2.2421 | 2.2421 |
| A split library must pass under every possible allocation | 3 | 6 | 2 | 0.5034 | 0.5034 |
| Passing depends on the allocation of alternate reads | 8 | 8 | 7 | 0.4330 | 4.3851 |
| Total | 37 | 64 | 14 | 3.1786 | 7.1307 |

The eight sites in the third row each contribute exactly one scored comparison. At four of them, the two aliquots together contained five alternate reads. With no five-read witness elsewhere in the flower table, a site could pass the screen only if all five fell in one aliquot. All four observations were one-sided by that requirement. For the other 29 sites the five-read condition places no restriction on the allocations. Seven of their 56 scored comparisons were one-sided, against 2.746 expected under uniform allocation. [Per-site results](gate_result.json)

## Conditional calculation

For a single site, hold every pair’s two read depths and pooled alternate count fixed. Hold alternate counts in the other flower libraries fixed. For pair j let X be the number of its k alternate reads allocated to the first aliquot. Under uniform allocation to the a+b read positions,

$$
P(X=x)=\binom{a}{x}\binom{b}{k-x}/\binom{a+b}{k}.
$$

Write $O_j$ for the event that the pair is scored ($k\ge2$) and all its alternate reads fall in one aliquot. Write $F_j$ for the event that both aliquots have fewer than five alternate reads. The probabilities $s_j=P(O_j)$, $f_j=P(F_j)$ and $u_j=P(O_j\cap F_j)$ follow from this distribution. When $k<5$, $u_j=s_j$. When $k\ge5$, $u_j=0$.

If an outside flower library already passes, the expected one-sided count is $\sum_j s_j$. Otherwise, under independent allocation across pairs within a site, the probability that the site passes is $g=1-\prod_j f_j$. For $g>0$ its conditional expected count is

$$
\frac{\sum_j\left(s_j-u_j\prod_{i\ne j} f_i\right)}{g}.
$$

In these data each allocation-sensitive site has only one scored comparison and only that comparison can supply five reads. Other pairs at the site have at most one alternate read. Its conditional answer therefore follows directly from the single-pair distribution. Summing the site-local conditional expectations gives the benchmark above. Interpreting that sum as conditional on the selection of *all* sites together additionally requires a joint model for selection across sites, such as independent allocation across sites.

This reconstructs one numerical condition on counts in retained rows. The original pipeline included additional quality and filtering criteria and visual inspection. Rejected sites and the complete prefilter counts are unavailable here. Consequently this exercise quantifies how one specified screen affects the benchmark on the released margins. The remaining difference of 6.87 does not identify a biological cause, a contribution of the full discovery pipeline, or a calibrated false-negative rate.

## Reproduction

The two programs use Python’s standard library. From this directory run the following commands. The influence extraction reproduces the input profiles from the original published workbooks and keeps the other 30 flower libraries distinct from the 40 split libraries. The 669 pairs with zero pooled alternate reads and seven pairs with a single read can neither contribute to the scored endpoint nor supply five reads. [Input profiles](../influence/influence_profiles.json)

```sh
python3 -B gate_conditioning.py | diff - gate_result.json
python3 -B verify_gate.py
```

The second program enumerates every allowed subset of read positions in 1,840 small configurations, including passes supported by different pairs, impossible passes and passes guaranteed by outside evidence. The production calculation uses exact rational probabilities and rounds only the saved numeric summaries.
