# Forecast rules for measured lineage abundance

## Question and scope

Does the most abundant identified label at an early visit retain first place at the final scheduled visit? Does the change in abundance between the first two visits improve the forecast? This is a retrospective benchmark on published records. Establishing the identity of a newly arisen causal mutation requires additional evidence. The older TMD first-arrival analysis has a distinct endpoint.

We selected two candidate studies on design before looking at their leader scores. The first is Fasanello et al. (2020), with two distinguishable founder labels in laboratory yeast populations. The second is Levy et al. (2015), with many lineages. Score all populations in the source condition with a stable label namespace, a scheduled baseline, at least three distinct visits, and numeric label counts or measured shares. Document source exclusions and any complete-case loss. Analyze studies separately. Technical replicates, repeated assays of the same population, and shared founders require explicit identification. Declare the input table and eligible rows before computing scores. If the original data support only relative abundance, exact transferred-read sensitivities require an independent count table.

## Fixed rules

For population p, let x(t,i) be the observed share of all assigned counts belonging to label i at scheduled visit t. Use the study's reported share if counts are unavailable. Let b and e denote the first and second scheduled visits, and f the final visit. Use the same predeclared times in every comparable population. A missing or zero-total required visit yields an unscorable population. An absent label can take value zero only where the data format represents a genuine zero count.

1. The baseline rule predicts the label with the largest x(b,i).
2. The early leader rule predicts the label with the largest x(e,i).
3. The early change rule predicts the label with the largest 2x(e,i) − x(b,i). This projects the observed change forward by one early interval as a ranking score, without fitting its coefficient to the final data. It may take values outside the unit interval.

At each issue time consider labels with positive counts by that time. Compare predictions with the labels attaining the highest measured share at f among *all* assigned labels, including entrants. A tied prediction abstains. A unique prediction earns a strict hit only if it equals the unique final leader. Report tied endpoints and joint-first separately, along with missing visits, denominator, and coverage. Compare the last two rules on the same populations and report discordant successes in both directions. Treat any comparisons on additional visit schedules, alternative score definitions or other studies as exploratory.

For a two-label population with both labels eligible and a unique final leader, guessing each label with equal probability has expected score one half. For K eligible labels and a unique final leader, the corresponding expectation is 1/K if the final leader is eligible and zero otherwise. This is a guessing reference. It does not model neutral drift or establish a biological effect. Describe any shared design or acquisition bias that could explain success. No significance test assumes that technical reads or all rows are independent.

The plan was written using design descriptions, before calculation of the leader scores. The records were already public. This is an internal freeze for a retrospective comparison.
