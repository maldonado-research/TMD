# Can the records establish which route led?

A pipeline can prefer one route simply because it misses more examples of another. This retrospective audit asks which route was most frequent among the units on **one fully enumerated roster**. It retains all pipeline outcomes and uses independent reference labels wherever they exist. It reports a leader only if its true count exceeds both competitors throughout the simultaneous set of admissible counts.

A route that leads on this roster could reflect mutation supply, establishment, selection or the choice of roster. Quantifying observation error addresses one part of that interpretation. A population forecast or causal test requires a design linking the roster to that target. The archived 0.7.0 inference uses future-unit probabilities conditional on a frozen pipeline. Substituting finite-roster percentages into its transport bounds requires an additional sampling or generalization argument. [Archived integrated method](../integrated_inference/README.md) · [Transport sensitivity](../transport_sensitivity/README.md)

## A reversal with one label still missing

In a constructed roster, the 10 W calls, eight A calls and two M calls are all independently confirmed. Five further records failed the gate. Before any of those five receive reference labels, W minus A ranges from −3 to +7. Assigning all five to A or all five to W realizes the two extremes.

Four of the five gate failures then receive independent A labels. Now A has at least 12 records, W has at most 11 and M has at most three. **A must lead**, however the last record resolves. This conclusion holds even if the four records were chosen deliberately. The result turns on what the four labels establish about these 25 records. [Synthetic reversal input](synthetic_reversal.json)

## What goes into an audit

Use one unit definition, one context and arm, a frozen pipeline, and a frame that includes every unit before gating. Record the frame membership, one gate outcome and one pipeline label per unit. Keep an auditable link from sampled units to independently assigned reference labels. Define the reference rubric and how reviewers are blinded to the pipeline call. Shared measurement errors or incorrect reference labels can distort all inferences against biological truth.

The five output rows are W, A, M, passed but unresolved (U_pass), and failed (U_fail). Each sampled record has one reference label W, A, M or Other, or an unavailable reference label. These last two outcomes have different meanings. In each row supply its frame size N, count selected for review n, and four verified reference counts y. The number of missing reference labels is n minus their sum. A zero-size or unaudited row still appears in the input.

Use `unspecified` when selection probabilities are unknown or records were deliberately chosen. With a complete frame and correct resolved labels, the deterministic count bounds hold for any review mechanism. Use `stratified_srswor` only with a fixed sample size and simple random sampling without replacement within each frozen row, established from the sampling record. The program checks arithmetic. Unit identity, frame completeness, the sampling law and reference validity require external evidence.

## How the bounds work

Let K be the number of units of reference class t among the N units in a row. With a simple random sample of n, the latent complete sample count X has a hypergeometric distribution. Across five fixed rows and four reference classes, split the total error probability α equally across 40 tails. Retain K when both inclusive tail probabilities at the complete count are at least α/40. The code evaluates integer counts of subsets and compares them to the exact rational threshold.

With y verified cases and r missing reference labels, the complete sample count can range from y to y+r. Monotonicity in the observed count gives the lower endpoint at y and the upper endpoint at y+r. Equivalently, the upper endpoint is N minus the lower endpoint for n−y−r verified nonmembers. The actual complete sample count is among these possibilities for every missingness pattern. For unspecified selection the corresponding count bounds are simply [y, N−sum(other verified counts)].

Intersect the resulting integer box with the known total in each row. For coordinate t with initial bounds [l_t,u_t], the tightened bounds are

    L_t = max(l_t, N − sum of other upper bounds)
    U_t = min(u_t, N − sum of other lower bounds).

The true table belongs to this set with probability at least 1−α over the declared random draws. This follows by adding up the 40 tail error bounds and requires no independence of confidence events. For unspecified selection the set contains every completion consistent with the verified counts. Multiple rosters require an error allocation across the collection if a joint probability statement is intended. Choosing which roster or pipeline to report after seeing its labels changes that guarantee.

For two routes i and j, the smallest within-row difference is L_i−U_j and the largest is U_i−L_j. To see why the upper endpoints can be attained together, consider the permitted total of the remaining coordinates. Attainability of U_i and L_j individually puts N−U_i−L_j between their aggregate lower and upper bounds. Every integer between those aggregate bounds can be allocated. Exchanging i and j gives the lower endpoint. Add the differences over rows to obtain the roster range. A strict leader must beat each rival even at its least favorable difference. These extrema are sharp within the constructed set. The marginal confidence construction and the separate treatment of missing counts by class can enlarge that set.

For each class, sum its count bounds separately over rows of interest and their complement. If those counts are a and b, the fraction of interest is a/(a+b). It increases with a and decreases with b. Report endpoints among positive denominators and a separate flag whenever class absence is possible. The numerator for a true Other passing the gate includes U_pass. A correct route call uses only the matching call row in its numerator and every record of that true route in its denominator. The guarantees concern the observed roster and the declared reference labels.

## A random-audit example

In the [synthetic 100-record example](synthetic_input.json), all 70 gate-pass records are reviewed. Of the 30 gate failures, 15 are selected by simple random sampling and one review is inconclusive. On this input the simultaneous 95% bounds for the fraction of true Other that passed are [1/3, 13/25]. The same records under unspecified selection give the wider deterministic range [1/3, 13/23]. The random-audit bounds for W minus A are −11 to +14, leaving their rank unresolved. [Saved output](synthetic_result.json)

## Sources and reproduction

The [published-data checks](SOURCE_ASSESSMENT.md) describe what can be measured using existing plant mutation records and where the reference labels end. The finite-population distribution, test inversion, union bound and missing-label completion are established statistical techniques. A 2026 preprint presents a related two-phase verification design in health records. Its complete-review assumption motivates handling inconclusive reviews explicitly here. [Wang, JASA](https://doi.org/10.1080/01621459.2014.966191) · [Tang et al., preprint, §§3.1–3.3](https://arxiv.org/html/2610.12059v1)

Run from the repository root with Python 3. The method and its independent enumerative verifier use the standard library.

```sh
python3 -B research/finite_roster_audit/audit.py research/finite_roster_audit/synthetic_reversal.json
python3 -B research/finite_roster_audit/audit.py research/finite_roster_audit/synthetic_input.json
python3 -B research/finite_roster_audit/verify_audit.py
```

The [independent enumeration](verification.json) checks 1,980 cell intervals, 1,386 integer-row projections, 441 fraction ranges and 5,388 joint tables. It includes equality at the exact tail threshold, missing reviews and empty reference classes. One illustrative joint design covered the true table over 20,580 of its 20,592 equally likely draw pairs under every tested masking choice. That frequency describes this fixture.

Prepared on 18 November 2026 with AI assistance and internal computational review. The two W/A/M examples are constructed. The native TMD audit still requires a linked roster and independent labels.
