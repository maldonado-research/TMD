# Does the Kennedy result single out early windows?

The trained six-class spectrum beat the equal-six reference for every admissible first-class assignment on the seven continuing paths. A common class can also appear in a window simply because it makes up much of that pedigree's recorded catalog. This exploratory analysis asks how often a window of the same size, drawn from each path's own calls, would have a worst-case Brier gain at least as high as the actual early windows. The check was added after the primary results were available. [Primary design](../DESIGN.md) · [Event roster](../kennedy/kennedy_events.tsv)

| Quantity | Result |
| --- | ---: |
| Observed mean lower Brier gain over equal-six | +0.07033 |
| Expected mean lower Brier gain under random windows | −0.00830 |
| Exact one-sided probability of an equal or higher gain | **0.18313** |
| Range after assigning the one unlinked later F call to each possible class | 0.16760 to 0.20275 |

The observed windows scored above the random-window average. Under this particular exchangeability model, windows at least this favorable occur about 18 times in 100. The gain over equal-six therefore supplies limited evidence for an additional association with early timing after conditioning on the recorded composition of each path.

## What is held fixed

The seven typed pools contain 19, 41, 36, 30, 30, 32 and 30 calls on paths B, C, D, E, F, G1 and H. Hold their first-window sizes fixed at 2, 3, 2, 2, 3, 1 and 7, and sample that many site calls uniformly without replacement within each pool. The model samples the seven windows independently. Every site is distinct at this stage, including sites of the same substitution class. The scoring step uses the least probable admissible class among the selected sites. Holding out the entire founding family for training reproduces the primary forecast. Randomizing the time positions leaves its training totals fixed. G2-specific calls enter training when another family is held out. The primary G test uses the continuing G1 path. [Primary comparison](../README.md)

The main calculation omits the single unlinked later F call from its typed pool and from the training counts. Its archived position is outside F's first window. The sensitivity analysis assigns each possible class to that same event, includes it in the F pool and recalculates all affected training forecasts. Different probabilities of recovery or of different classes across divisions, persistent mutation-rate states, and relationships among calls within divisions could all violate exchangeability. The tail probability describes the specified random-window mechanism conditional on these observed catalogs and window sizes. It does not estimate the chance that the biological hypothesis is true.

## Exact enumeration

Group a pedigree's typed sites by their forecast probability. For each distinct probability $v$, let $m_{\ge v}$ count sites of probability at least $v$, and $m_{> v}$ those strictly above it. Among all size-$k$ subsets, the number with minimum exactly $v$ is

$$
\binom{m_{\ge v}}{k}-\binom{m_{>v}}{k}.
$$

Use zero for a binomial coefficient with fewer than $k$ available sites. For the equal-six reference the lower Brier gain of a subset with minimum $v$ is $2v-\sum_c p_c^2-1/6$. The fold-specific constants cancel when comparing randomized and observed sums. Combining the seven minimum-value distributions gives **24,197,124,922,452,690,243,360** equally weighted subset combinations at or above the observed gain out of **132,127,812,049,903,488,000,000**. Direct arithmetic includes equality and yields the reduced fraction $298288029122937503/1628794527242400000$. This is the exhaustive conditional tail without simulation error. [Exact counts and sensitivity results](random_window_results.json)

Run both commands in this directory with Python 3.10 or newer. The independent check scores every eligible class from the original squared losses, counts subset minima by adding events one by one and convolves the seven resulting score distributions. It verifies the observed and expected gains and both full integer counts for each sensitivity case.

```sh
python3 -B random_windows.py | diff - random_window_results.json
python3 -B verify_random_windows.py
```
