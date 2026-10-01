# TMD research extension 0.3.0: Can we separate evolution from measurement bias?

**Ricardo Maldonado · exploratory methods update · 30 September 2026**

Some mutation routes may be easier to recover and count than others. That can distort a test of Mutation by Natural Dominance. This update develops a four-sample method that adjusts for independently measured route recovery, includes uncertainty in the controls, and shows how the conclusion changes when controls do not fully match biological samples.

## Download the complete reviewed package

- [TMD research extension 0.3.0 ZIP](TMD_research_extension_0_3_0_2026-09-30.zip)
- [Archive SHA256 checksum](TMD_research_extension_0_3_0_SHA256SUMS.txt)

The ZIP contains **42 files**: complete source code, mathematical derivations, independent review notes, synthetic examples, a four-paper literature update, transport sensitivity, design planning, a prospective data contract and licensing. Its SHA256 is:

```text
224d292575a93afca6f5912ed2536f51ca0f42555f6b2ddd4e1bcd4e53af1753
```

Extract it and open `research_extension_0_3_0/README.md`. Python 3.10+ and NumPy support inference; the planning helper uses the standard library. **25 automated checks passed**: 16 inference checks and 9 design checks. An independent agent review checked the algebra, observation contract and code, and independently audited the repeated-sample results. This is internal review, not external peer review.

## In More Basic Terms

Imagine a sorting machine that catches most blue marbles but misses many red ones. Counting what comes out could make us believe red marbles were rare to begin with. Biology can have the same problem: the way we measure a mutation route can affect how common it appears.

We now combine four separate groups for each condition: a biological baseline, selected outcomes, baseline recovery controls and selected recovery controls. The controls must have independently known starting mixtures and a valid sampling design. Their recovered counts have uncertainty too, so the calculation includes it.

In constructed examples, the correction removes an apparent difference caused by recovery bias while preserving a real difference between conditions. The next challenge is whether laboratory controls actually match evolving biological samples. The package makes that assumption explicit and provides bounds for imperfect matching.

## What the mathematics adds

With route order Wsp, Aws, Mws and contrast weights v=(−1/2,1,−1/2), the adjustment is:

```text
theta_corrected = v · [log(selected) − log(baseline)
                       − log(selected_control) + log(selected_input_mixture)
                       + log(baseline_control) − log(baseline_input_mixture)]
```

Under justified transfer of route-relative recovery, this equals the biological supply-adjusted contrast. Common assay-wide recovery scales cancel; absolute efficiencies and the causal mutation/fitness/accessibility decomposition remain unidentified. A convex joint likelihood compares a shared contrast across contexts with a saturated four-arm alternative; its regular restriction count is C−1. One context alone cannot test sharing.

The method requires independent categorical units and independently known positive **randomized** control input compositions. Fixed per-route introduced totals with recovery successes require a different binomial likelihood. Fluctuation colonies, pathway-isolated strain totals, amplified barcode reads and shared-batch observations cannot simply be relabeled as independent samples. Input declarations do not authenticate an experiment.

All observed zero cells are conservatively unsupported in this prototype; this does not assert that every zero has a boundary MLE. The approximate fitted-null bootstrap resamples all four arms, preserves totals and retains unresolved draws in computational p-value bounds. It is not an exact finite-sample test.

## What the synthetic checks show

A deterministic four-context fixture has shared true theta=log(2) but different route recovery. Ignoring recovery produces deviance 695.10 and approximate bootstrap p=.005. Joint correction recovers the common contrast, deviance 0 and p=1. A second fixture changes the fourth biological contrast to log(4); the corrected test retains that departure, deviance 20.79 and p=.005. Each comparison uses 199 bootstrap draws. The p=1 result comes from an intentionally noiseless construction; the minimum .005 values have only 1/200 Monte Carlo resolution.

Separate repeated-sample checks used 40 random datasets per scenario, four contexts, 600 observations per arm/context and 99 bootstrap draws per dataset. The shared-contrast scenario rejected **0/40** at 5% (95% Wilson interval 0–8.76%); the context-departure scenario rejected **24/40**, or 60% (interval 44.60–73.65%). All 80 datasets and 7,920 bootstrap draws resolved. No failed dataset or draw was replaced or discarded. Independent review reproduced all dataset counts and six complete bootstrap runs.

These results concern two selected designs. They do not certify general test size or power. The true departure was missed in 16 of 40 random studies, which makes the need for actual design calibration visible. No included number is a new biological observation.

## When controls do not fully match

The corrected contrast equals the biological contrast plus a differential transport-bias term. If no defensible transfer argument or finite bound exists, biology and that bias remain confounded. The sensitivity tool gives sign-aware biological-contrast bounds for justified routewise mismatch limits. Overlapping intervals show compatibility under assumptions; they do not confirm TMD.

Four independent equal-frequency groups with 100 recovered observations each give an approximate standard error of .4243. Pretending the measured controls are perfectly known would give .3000. Including their uncertainty makes it about 41% larger. This is an analytic planning example, not a prescribed experimental sample size. Cost-aware allocation counts recovered independent units and needs real recovery-yield and laboratory cost assumptions.

## What the new source review contributes

Four previously unreviewed primary studies inform the measurement design: [McGee et al. (2024)](https://academic.oup.com/mbe/article/41/8/msae152/7718338) on barcode processing bias; [Abreu et al. (2024)](https://www.nature.com/articles/s41559-024-02475-9) on environmental memory; [Lansch-Justen et al. (2024)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012146) on heterogeneous-stress mutation-rate inference; and [Rehm et al. (2026)](https://www.nature.com/articles/s41587-025-02944-x) on independently calibrated engineered replication. None validates WS control transport or TMD. The package records publication dates, limited read scope and which design suggestions are our inferences.

The scoped local archive audit found detection-bias cautions, generic spike-in requests and blank assay templates, but no authenticated independent matched recovery measurements. Original references were preserved. The next priority is a real independent baseline assay, matched controls challenged with held-out mixtures, defensible transport bounds and a biological forecast locked before new selected outcomes.

## Versions, scope and reuse

This package is **0.3.0**. [Methods extension 0.2.0](TMD_RESEARCH_EXTENSION_0_2_0.md), the [expanded 0.1.0 report](https://zenodo.org/records/23068056) and [historical software v2.6.5](https://zenodo.org/records/22398093) remain separate records. No earlier DOI identifies this package; use its version-specific `CITATION.cff` and cite primary papers separately.

No new laboratory experiment, confirmed mechanism, unified physical theory or external mathematical priority is claimed. This advance is a reproducible measurement-aware test with sharper empirical requirements. New code is MIT licensed, new writing is CC BY 4.0, and third-party rights remain intact. AI assistance was used under Ricardo's direction. Neither EDISON nor MOSBRI funded TMD.
