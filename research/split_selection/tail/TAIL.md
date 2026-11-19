# How much does agreement across comparisons matter?

Fourteen of 64 scored comparisons in one peach flower had all their alternate reads in one split. The published read depths specify a marginal probability of that outcome under a uniform-allocation benchmark. A second benchmark uses an inclusive five-read proxy for one step in discovery. The Methods and supplementary wording differ at exactly five reads. [Source assessment](../source/ASSESSMENT.md) The probability of 14 or more one-sided outcomes still depends on how those indicators vary together. The same tissue, site or preparation can contribute to many comparisons. [Peach study](https://doi.org/10.1371/journal.pgen.1011829)

| Marginal benchmark across the 64 comparisons | Expected one-sided count | Tail probability if the 64 indicators are mutually independent | Sharp probability range allowing arbitrary dependence |
|---|---:|---:|---:|
| Uniform allocation at the recorded split depths and alternate totals | 3.17860 | 0.0000001023 | 0 to 0.193256 |
| Allocation accounting for the five-read candidate gate alone | 7.13071 | 0.00024199 | 0 to 0.292093 |

The gate alone forces four one-sided outcomes. Accounting for it and leaving cross-comparison dependence unrestricted allows the observed count or a larger count to occur with probability as high as **29.21%**. Both endpoints in each row are attainable. Every intermediate value can be attained by mixing the two endpoint distributions. These calculations describe a fixed list of marginal probabilities. They do not measure the probability that chance explains the flower or the frequency of a missing mutation.

## How the gate enters

For each pair fix its two depths and its pooled alternate count. Uniformly distribute the alternate labels among the read positions. The number in split A then has a hypergeometric distribution. First check the maximum count in the 30 other flower libraries at the same site and the feasible counts in all pairs. In 26 sites a different library already reaches five, and in three more sites at least one pair reaches five for every feasible allocation. At each of the remaining eight sites exactly one pair can reach five in either half. For each of these eight pairs, restrict its hypergeometric distribution to allocations with at least five alternate reads in one half and normalize. For the others keep the uniform-allocation marginal. The scripts verify the eight updates by two independent calculations.

These are stipulated marginal laws on the whole selected frame. They would follow for the gate alone under independent pre-screen allocations, fixed outside-library evidence and the specified gate. Allowing arbitrary dependence **after** stipulating these marginals gives the range above. Applying all gates to arbitrarily dependent pre-screen allocations could change even the other pairs’ marginals. Additional source filters, sampling dependence within a pair and local variation in composition can also change them. None of the tail values is a calibrated significance test of the ascertained flower or of biological TMD.

## Why the upper limit is sharp

Let S count the successes of n binary indicators with probabilities ordered q₁ ≥ … ≥ qₙ. For any integer j from zero to r−1, at least r−j successes must occur outside the first j indicators on the event S ≥ r. Taking expectations gives the following established sharp upper bound.

$$
U = \min\!\left(1,\min_{0\le j<r}\frac{\sum_{i=j+1}^{n}q_i}{r-j}\right).
$$

In the first row the optimizing cut omits four probabilities. In the second it omits five, including the four equal to one. Dividing the total mean by 14 alone gives 0.22704 and 0.50934, respectively. The full formula was derived by Rüger and Morgenstern and appears as equation 7 in Padmanabhan and Natarajan. [Published paper](https://doi.org/10.1287/ijoo.2019.0038) · [Equation 7 and original references](https://arxiv.org/html/1910.06321v1#S1.SS2)

For 0 < U < 1, let a tail event have probability U. Inside it assign conditional inclusion probabilities min(qᵢ,U)/U. These sum to r by the minimizing cut, so one can select exactly r indicators. Outside it use max(qᵢ−U,0)/(1−U). Fewer than r of these latter probabilities are positive. Mixing the inside and outside assignments returns each original qᵢ and attains U. The verifier constructs each conditional assignment by laying intervals of the desired inclusion lengths end to end and placing a unit-spaced grid at a uniform random offset. Each interval is hit with its specified probability. When the summed length is an integer, every offset apart from endpoints gives exactly that many hits. Applying the same upper-bound calculation to failures gives the sharp lower bound for successes. The verifier checks exact marginal and tail masses for both endpoints in both rows.

## Reproduce

The scripts take the workbook-derived `influence_profiles.json` in this checkpoint. Run from the directory holding these scripts and supply the path to that file. The input SHA-256 and exact rational results appear in the receipt. Python 3.10 or later suffices.

```sh
python3 -B peach_tail.py /path/to/influence_profiles.json | diff - tail_result.json
python3 -B verify_tail.py /path/to/influence_profiles.json tail_result.json
```
