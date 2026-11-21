# Did each marker benefit from its own parental measurement?

For the 17 offspring-discovered mouse variants, we kept the offspring observations and every parental fraction fixed. We asked how well each fraction would have scored if assigned to a different marker in the same family. Positive gain means lower binary Brier loss than using that marker’s frequency in the ten discovery pups. We specified the control before reviewing the parent-forecast scores. [Control specification](../MATCHED_MARKERS.md) · [Mouse data](../mouse/README.md)

| Parental fractions could be exchanged within | Labeled assignments | Fraction at least as good as the actual pairing | Observed gain minus average shuffled gain |
|---|---:|---:|---:|
| Family | 14,631,321,600 | 0.65873 | −0.000343 |
| Family and discovery-pup carrier count | 622,080 | 0.60813 | −0.000168 |
| Family, discovery-pup carrier count and parent | 207,360 | 0.60006 | −0.000168 |

The second comparison holds fixed the discovery frequency available to the predictor. Five groups contain the 17 markers. Four groups have more than one marker and distinct parental fractions. **378,304 of 622,080 assignments** scored at least as well as the actual one. Using the carrier total from the alternative source workbook gives 374,180 of 622,080. Variants tracing the same developmental lineage can share biology and observation errors. These tail fractions describe the allowed assignments in the two observed families.

### What the two forecasts contribute

Let p be the parental fraction, q the discovery frequency and r the held-out carrier fraction. Calculate covariances and variances within each group with population denominators, then average them by the groups’ total analysis weights. Since the sum of squared parental predictions is fixed under permutation, the gain of the actual assignment over the average shuffled assignment is twice the within-group covariance of p and r. The gain over using the *mean parental fraction* in each group is twice the covariance minus the within-group variance of p. For the second row above, this latter gain is −0.000864.

As a descriptive decomposition after scoring, the fixed average of the parent and discovery forecasts satisfies

$$
B(q)-B((p+q)/2) = [B(q)-B(p)]/2 + (p-q)^2/4.
$$

Here B is binary squared loss evaluated on the same offspring. The identity holds after averaging over markers and families. Half the parent gain is −0.000468. The quarter squared-disagreement term is +0.005186, giving the observed midpoint gain of **+0.004719**. Within groups with the same q, random reassignment of parental fractions gives an average midpoint gain of **+0.004803**. In this discovery-selected panel the two forecasts generally miss in opposite directions, and averaging improves the score even after the parental labels are shuffled. [Calculations](results.json)

Run from this directory with Python 3.9 or newer. The enumerator counts all within-family dot products using integers, then combines the two families with cumulative counts. It preserves ties and checks the covariance identity with rational arithmetic.

```sh
python3 -B marker_pairing.py | diff - results.json
```
