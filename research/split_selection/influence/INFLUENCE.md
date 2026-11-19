# Which groups contribute the excess of one-sided peach observations?

The 64 eligible comparisons in peach flower #2 contained at least two alternate reads across their paired splits. Fourteen had every alternate read in one half. Uniform allocation at the two recorded depths predicts 3.17860, giving an excess of 10.82140. Every leave-one-site, leave-one-tissue and leave-one-organ comparison retains a positive excess. The result is more concentrated across tissues than across sites. [Ji et al.](https://doi.org/10.1371/journal.pgen.1011829) · [Aggregate results](influence_result.json)

| Groups removed as a unit | Groups with eligible records / all | Positive, negative, zero group contributions | Excess after removing any one group | Fewest removals allowing an excess of zero or less |
|---|---:|---:|---:|---:|
| Candidate site | 21 / 37 | 13, 8, 16 | 9.823 to 10.949 | 13 |
| Split tissue | 20 / 20 | 6, 14, 0 | 6.290 to 11.071 | 5 |
| Organ class | 4 / 4 | 3, 1, 0 | 4.363 to 10.887 | 3 |

In the petal tissue labelled Pair12, five of seven eligible comparisons were one-sided, against 0.469 expected. Across all petals, eight of 31 were one-sided against 1.542 expected. Stamens contributed four of 15 against 0.908, sepals two of 16 against 0.663 and the carpel zero of two against 0.066. These counts describe tissue contributions within a single flower. The four organ classes have different numbers of samples and sites.

For each comparison let O be the one-sided indicator and q the probability that all observed alternate reads fall in one half under uniform allocation without replacement. With split depths a and b and k alternate reads, q equals [C(a,k) + C(b,k)] / C(a+b,k). Group contributions sum O − q over disjoint cells. To minimize the retained excess after a given number of deletions, remove groups with the largest contributions, while retaining at least one cell with 0 < q < 1. The calculation tries each informative group as a retained group in turn. The size bound is exact because exchanging a removed smaller contribution for an available larger one cannot increase the retained excess. A second implementation checks the optimum by a subset recursion. All comparisons and ordering use exact fractions. Numerical results in the tables are rounded.

## Were these sites also seen outside the scored splits?

The authors deposited 30 other flower #2 tissue libraries in the same S3 read-count block. Each has a unique identifier and no split-pair label. The 40 libraries used in the score and the 10 samples labelled adjacent leaf are outside this comparison set. We retained the original 37 discovered sites and described how much split imbalance appears at sites with varying evidence in these 30 libraries. This restriction still uses the original study’s discovered-site list and the same flower. [Table S3](https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s017.xlsx) · [Extracted profiles and outside evidence](influence_profiles.json)

| Evidence in the 30 other libraries | Sites with that evidence | Eligible split comparisons | Observed one-sided | Expected | Excess |
|---|---:|---:|---:|---:|---:|
| At least one alternate read in one library | 29 | 53 | 6 | 2.416 | 3.584 |
| Zero alternate reads in all 30 libraries | 8 | 11 | 8 | 0.763 | 7.237 |
| At least two alternate reads in one library | 27 | 51 | 5 | 2.308 | 2.692 |
| At least one alternate read in each of two or more libraries | 9 | 47 | 5 | 2.171 | 2.829 |
| At least five alternate reads in one library | 26 | 50 | 5 | 2.242 | 2.758 |

Eight sites with zero outside support account for 7.237 of the total 10.821 excess. An absence of reads in these other library samples leaves within-flower location and detection unresolved. Among sites with at least five reads in one outside library, one can remove any single site or tissue and retain a positive excess. Removing two tissues (Pair3 and Pair18) leaves one one-sided comparison in 43 against 1.525 expected, reversing the sign. These retrospective sensitivities characterize the discovery data. The prospective test on an independent archive remains open.

## Reproduction

From the directory containing this note, run the following commands. Only the original-workbook extraction requires openpyxl. The saved profiles also reproduce the group results offline using the Python standard library. Compare the eligible profiles against the earlier archived `allocation_profiles.json` by passing its path to the verifier’s optional `--previous` argument.

```sh
python3 -B extract_influence.py /path/to/S2.xlsx /path/to/S3.xlsx /path/to/S5.xlsx | diff - influence_profiles.json
python3 -B influence.py | diff - influence_result.json
python3 -B verify_influence.py
```
