# TMD research extension 0.4.0: What went in, and what came back?

**Ricardo Maldonado · exploratory methods update · 30 September 2026**

Some evolutionary routes may be easier to recover and count than others. This update adds a calculation for controls that start with a known number of units separately for each route and retain both successes and failures. It also checks whether proposed counts and budgets can support the current test.

[Download the complete 0.4.0 package](TMD_research_extension_0_4_0_2026-09-30.zip) · [Verify its checksum](TMD_research_extension_0_4_0_SHA256SUMS.txt)

Extract the ZIP and start with `research_extension_0_4_0/README.md`. The package contains code, methods, the input contract, synthetic examples, planning calculations, literature notes and independent internal review. The citation inside the package identifies this version.

## In More Basic Terms

Imagine comparing three routes through a maze. Counting travelers at the exits does not tell you whether more chose one route or whether that route was easier to observe. The new controls record how many independent units went in and how many met the chosen recovery rule. That helps adjust the comparison and includes uncertainty in the adjustment.

The controls still need to match the real observation process. A control cell does not automatically behave like an evolving cell. A repeated camera reading, a sequence read or an unverified sorting event cannot simply become a new independent cell trial.

There is also a practical surprise: if recovery is almost perfect, a small control sample may contain only successes. The current conservative test declines those tables. That is a limitation of this version, not a reason to want worse recovery. Our new planner makes the limitation visible before recommending counts.

## The mathematical advance within this project

Version 0.3.0 used recovered labels from known input mixtures. Version 0.4.0 instead combines two biological three-route samples with six independent route-specific binomial controls per context. Each control records known introduced and recovered totals. These designs have different likelihoods and cannot exchange inputs silently.

With route weights v=(−1/2,1,−1/2), observed baseline/selected probabilities b,t, and control recovery d0,d1, the corrected contrast is:

```text
theta = v · [log(t) − log(b) − log(d1) + log(d0)]
```

The joint negative log likelihood is convex in log-recovery coordinates, with linear multinomial logits. A shared-contrast model has 9C+1 parameters and a saturated alternative has 10C; the regular restriction count is C−1. One context alone cannot test sharing. Introduced denominators identify absolute **control-process** recovery. Absolute biological recovery can retain unknown branch-wide factors under relative transfer. Route-specific mismatch remains confounded with the biological contrast.

The bootstrap resamples both biological samples and all six controls, preserving the exposed totals. It is a fitted-null approximate calibration. Unresolved draws stay in computational bounds. Categorical zeros, all-success/all-failure controls and numerical failures receive explicit declined results; no invented counts are added.

## What the checks show

All **30 automated checks passed**. Independent internal review checked derivatives, identification, numerical behavior, uncertainty, exact count-policy probabilities, constrained allocation and scientific scope.

Two exact synthetic fixtures show the intended behavior: a recovery artifact disappears after correction, while a deliberately changed contextual contrast remains detectable. Each uses 199 bootstrap draws; the minimum reported p=.005 has 1/200 Monte Carlo resolution.

An additional study retained **120 random simulated datasets**. With 99 bootstrap draws per admitted study, it rejected 1/40 shared-contrast datasets and 33/40 deliberate-departure datasets. Their approximate 95% Wilson intervals are 0.44–12.88% and 68.05–91.25%. All 7,920 attempted draws resolved. These are limited fixed-scenario diagnostics, not certified general size or power.

In the high-recovery scenario, all 40 datasets were declined because a control had only successes or only failures. **No tests were performed in those 40 studies.** The model-based probability of all 24 controls passing the interior-count policy is about 0.001777% at recovery .99 and 100 introduced units each. A separate high-precision calculation agrees.

## Plan precision and usable counts separately

Regular variance optimization alone can recommend counts too small for the supported inference. The planner adds component floors and explicit cap/budget failures. For an illustrative uniform biological composition, recovery .99, four contexts and a 95% global policy target, chosen equal-error floors are 19 biological observations per arm and 643 introduced units per control. Equal unit costs give 3,896 per context; budget 800 cannot meet those floors.

These floors are conditional on the stated true planning probabilities. They are not a universal cost optimum, a power target or a laboratory prescription. A validated boundary likelihood is a useful next extension for extreme controls.

## Evidence and the next real test

Four additional primary papers inform unit verification, culture endpoints, reference-material bias and genetic contingency, including [Petrungaro et al.'s July 2026 evolution study](https://www.nature.com/articles/s41467-026-76025-1). Measured findings are separated from our proposed design consequences in the package's attributed literature notes. No third-party raw data were analyzed or redistributed in this update.

A scoped local audit found no authenticated matched fixed-input W/A/M recovery panel. The priority remains real independent baseline and selected-route observations with known control units, successes/failures, preserved batch/culture lineage, and held-out recovery-transfer checks. Those measurements are necessary before interpreting a corrected contrast biologically.

This is a reproducible methods advance, with simulated validation and clearer empirical requirements. It does not establish a new biological mechanism, physical unification or external mathematical priority. New software is MIT licensed; new writing is CC BY 4.0. AI assistance was used under Ricardo's direction. Neither EDISON nor MOSBRI funded TMD.

[Earlier 0.3.0 overview](TMD_RESEARCH_EXTENSION_0_3_0.md) · [Repository](https://github.com/maldonado-research/TMD)
