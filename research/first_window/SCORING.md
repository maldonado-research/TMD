# How much does the unresolved order change a forecast score?

Suppose each eligible held-out pedigree has one latent first recorded substitution class. The archive restricts that class to a nonempty set $S_i$. Two sites of the same class supply one possibility for this target. A window with calls from only one class resolves the class even when it leaves the first site ambiguous. Unseen earlier mutations and simultaneous events that have no unique first member require a different target. The bounds below condition on a single first class among the eligible recorded calls.

## Paired gain

Let $p_i$ be a positive forecast vector, $q_i$ its positive reference, and $y$ a class in $S_i$. Positive gain favors $p_i$. For clarity the following formulas omit the pedigree subscript.

| Score | Gain for the same completed class $y$ |
| --- | --- |
| Multiclass Brier loss, summed over classes | $\sum_c(q_c^2-p_c^2)+2(p_y-q_y)$ |
| Natural log score | $\log(p_y/q_y)$ |
| Top hit with random choice among tied modes | $\mathbf1[y\in M_p]/\lvert M_p\rvert-\mathbf1[y\in M_q]/\lvert M_q\rvert$ |

Here $M_p$ and $M_q$ are the sets of maximizers. The top hit is the expected accuracy of the specified random tie rule. The Brier expression follows by subtracting the two losses $\sum_c(r_c-\mathbf1[c=y])^2$. The logarithmic and quadratic scores are strictly proper for a fully observed categorical outcome, meaning that its true probability distribution optimizes the expected score. [Gneiting and Raftery, 2007](https://doi.org/10.1198/016214506000001437)

For any one of these gain functions $g_i$, the sharp lower and upper endpoints for $n$ equally weighted pedigrees are

$$
L=\frac1n\sum_i\min_{y\in S_i}g_i(y),\qquad
U=\frac1n\sum_i\max_{y\in S_i}g_i(y).
$$

Every allowed completion has its mean between $L$ and $U$. Choosing an extremizer in each pedigree attains the corresponding endpoint if all those choices are jointly allowed. This argument concerns compatibility of class assignments. It requires no assumption of independent sampling. Any extra cross-pedigree constraint would require optimizing over the restricted set of joint assignments. Interior real values can be unattainable. The number of distinct class assignments is $\prod_i |S_i|$ under the product restriction. Their relative probabilities are unknown. This use of lower and upper expectations is an application of established random-set reasoning. [Dempster, 1967](https://doi.org/10.1214/aoms/1177698950)

Compute Brier endpoints with rational arithmetic. For log gain, multiply the smallest (or largest) $p_i(y)/q_i(y)$ from each unit. The log of that exact product divided by $n$ gives the endpoint. Comparing the product with one determines the sign exactly. Both forecasts must use the same hidden class. For example, identical forecasts produce zero paired gain for every completion even if their individual losses span a wide interval.

## What the equal-six reference implies

For $q_c=1/6$, Brier gain becomes $2p_y-\sum_c p_c^2-1/6$, and log gain becomes $\log(6p_y)$. Each of the three gains in the table is nondecreasing in $p_y$. Choosing the least probable admissible class per unit therefore gives a *common* assignment attaining all three lower endpoints. Choosing the most probable admissible class attains all three upper endpoints. The remaining width due to class ambiguity alone is

$$
U_B-L_B=\frac2n\sum_i (p_{i,\max}-p_{i,\min}),\qquad
U_{\log}-L_{\log}=\frac1n\sum_i\log(p_{i,\max}/p_{i,\min}),
$$

where the extrema range only over the classes in the earliest set. A ranking of the two forecasts on Brier loss is guaranteed when the lower gain is strictly positive or the upper gain is strictly negative. The score ranking depends both on the classes the archive allows and on how much probability the forecasts give those classes.

If all six classes appear in every earliest set and at least one trained forecast is nonuniform, the mean Brier and log bounds both extend strictly across zero. To see this for Brier, in each nonuniform unit $\min_c p_c<1/6<\max_c p_c$ and $1/6\leq\sum_c p_c^2\leq\max_c p_c$. Choosing the minimum gives a negative gain and choosing the maximum a positive gain. For log gain the corresponding strict signs follow from $\log(6p_y)$. Thus a large number of calls in each early window can still leave the sign unidentified.

A different, fully observed question selects one recorded site uniformly in the earliest window. If all eligible site classes and counts $m_{ic}$ in that window are known, its expected gain is $\sum_c m_{ic}g_i(c)/\sum_c m_{ic}$. The two ends of the chronological score range describe how far the actual first-call score could depart from that mean. Random site selection supplies no model of within-window temporal order.

## Relation to earlier project work

The project's 0.13.0 pedigree analysis measured which recorded calls could be ordered by their window and proposed retaining the possible first sites. Earlier project work also projected paired log-score differences over uncertainty in categorical probabilities. The present calculation projects scores over the possible observed first classes in held-out pedigrees. It addresses the forecast value of the archive's class labels. Testing establishment and the proposed supply-adjusted mechanism requires additional observations. [0.13.0 timing study](https://github.com/maldonado-research/TMD/blob/246d02bd66389ab50637f423dd62220aa852c754/research/pedigree_timing/README.md) · [Earlier score projection](https://github.com/maldonado-research/TMD/blob/246d02bd66389ab50637f423dd62220aa852c754/research/prospective_design/review/REVIEW_NOTES.md)
