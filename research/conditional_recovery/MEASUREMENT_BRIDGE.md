# Measurement bridge for differential-recovery sensitivity

Prepared as a focused internal evidence and nonredundancy review, 5 November 2026. All illustrative calculations here are synthetic. This review reuses the existing HiDenSeq source capture and independently assesses a newly acquired official SLST-Seq representation, summarized in [the source note](SLST_MEASUREMENT_NOTE.md) and `SLST_SOURCE_REVIEW.json`. No new biological measurement, native matched panel, author-code execution, outreach or registry change is reported. The preceding D-Blast3 inventory was not repeated.

## What is already covered

`research/transport_robustness/METHODS.md` already derives the diagonal-recovery identity `theta_corr,c = theta_bio,c + v·log(e_c)` for `v=(-1/2,1,-1/2)` and `e_ci=(r_1ci/r_0ci)/(d_1ci/d_0ci)`. It propagates residual boxes through `J=exp(2 theta)`, combines them with simultaneous count-confidence intervals, tests the cross-context intersection and finds an exact eighth-root compatibility frontier when every differential residual lies in `[1/R,R]`. It explicitly warns that a shared residual vector cancels from the equality restriction, whereas allowing a different vector in every context discards that coupling. Methods 0.6.0 integrates the pre-existing 0.3.0 recovery identity with the stored 0.5.0 confidence intervals; it does not introduce that identity.

`research/prospective_design/README.md` already calls for route/allele-by-phase-by-context controls, independent introduced denominators, assay-state challenges, transfer bounds and joint uncertainty allocation. It also says that contrast bounds cannot identify the entire observation map. `research/conditional_curvature/README.md` already states the uncorrected observed-curvature shift `delta_c` and warns that independent point estimates cannot replace unknown recovery with exactly known offsets.

The proposed addition is therefore a specific connection to the *two-context baseline-conditioned fiber*: evaluate the tail defined by the original reference ordering under the conditional law tilted by `t=exp[2(delta_2-delta_1)]`. That target and its fixed-reference tail differ from 0.6.0's projected common-J confidence intersection. The statistical ingredients remain standard conditional exponential-family and nuisance-sensitivity methods. Do not describe this as the first recovery robustness analysis, first common-curvature test, or a new biological mechanism.

## Which controls would justify a bound

Let `u_ci=r_1ci/r_0ci`, where `r_hci` is the probability that an eligible *true route i* outcome in context `c`, phase `h`, enters its correctly adjudicated observed route. This diagonal interpretation requires that false labels entering the other route categories have been excluded or separately modeled. Define

```
g_c = u_cA^2/(u_cW u_cM) = exp(2 delta_c)
t = g_2/g_1.
```

Only the cross-context difference of recovery curvature matters for this sensitivity parameter. A common route-independent recovery factor within a phase cancels; equal `delta_c` cancels even if the full recovery vectors differ. Absolute recovery is consequently sufficient measurement information, but not mathematically necessary. A scientifically validated direct bound on the same joint contrast can be more informative than twelve separate marginal intervals.

One transparent sufficient measurement design records the following for each of the twelve cells `phase {baseline,selected} × context {1,2} × route {W,A,M}`:

* A known true allele/route and common ancestral background, introduced at the actual boundary where the recovery process begins. Eligible introductions, successful correctly adjudicated recoveries, failures, wrong labels, unresolved outcomes and their denominators remain distinct.
* The actual introduced unit and amount, verified independently: an eligible lineage/outcome if that is the endpoint unit, rather than automatically a read, flow event, OD estimate, technical aliquot or a packet of unknown cells. If the calibration uses cells while the test samples run outcomes, their transfer requires explicit justification.
* Relevant matrix, abundance, physiological state, genotype, context, baseline/selected phase and batch. Late DNA spike-ins can calibrate extraction or sequencing after their insertion; they cannot calibrate earlier loss, establishment or growth. Controls introduced before establishment instead combine biological establishment with recovery unless the stages are separately measured.
* Blinded truth-based route adjudication, negative/blank controls and known mixed inputs to test false route assignment, contamination and composition-dependent performance. A zero observed false-call count does not prove an exactly diagonal population map.
* Independent calibration units or a justified alternative count model; preserve founder/batch/cluster identifiers. Repeated descendants and sequencing reads do not increase the biological trial denominator. A shared batch effect may prevent independent binomial trials even if every trial is binary.
* A prespecified route aggregation or allele-specific envelope. Different allele mixtures in the two phases can change effective recovery even when every allele's assay performance is stable.
* The rule and data supporting transport from introduced controls to actual native units, with an uncertainty or discrepancy bound that does not come from the selected endpoint discrepancy being tested.

For a justified binomial control law `K_hci ~ Bin(n_hci,d_hci)`, retain the raw known denominators and construct a simultaneous confidence region for the twelve population control probabilities. A Bonferroni allocation over valid marginal intervals is a conservative option; between-cell independence is not needed for that union bound. It does not repair invalid within-cell count laws. All-success finite samples still have a lower endpoint below one; zero successes can leave ratios unbounded. Prediction smoothing is not a replacement for these endpoints.

If controls identify the actual probabilities exactly in the relevant state, use `d=r`. Otherwise their role is explicit: `u_ci=(d_1ci/d_0ci)e_ci`, with scientifically supported residual transfer constraints on `e`. Without those constraints, precise `d` estimates alone do not bound actual `t`.

For a simultaneous rectangular region `0<l_hci<=r_hci<=U_hci`, define

```
a_ci = l_1ci/U_0ci
b_ci = U_1ci/l_0ci
g_c,lo = a_cA^2/(b_cW b_cM)
g_c,hi = b_cA^2/(a_cW a_cM)
t in [g_2,lo/g_1,hi, g_2,hi/g_1,lo].
```

These corner bounds are exact for the supplied rectangular set, not for every scientifically plausible joint calibration region. Shared controls, correlated constraints or direct contrast measurements may tighten them. Positive population recovery with confidence limits touching zero may yield the limiting range `(0,infinity)`; it does not permit silently clipping or smoothing the bound.

For transferred controls, project `t(d,e)` over the *joint* confidence and transport region. If each differential residual `e_ci` is bounded by `[1/R,R]`, the residual contribution to `t` lies in `[R^-8,R^8]`. If instead each separate phase ratio `r_hci/d_hci` is bounded by `[1/R,R]`, the differential residual can range from `R^-2` to `R^2`, and the cross-context multiplier is `[R^-16,R^16]`. These assumptions are materially different. A common residual curvature in both contexts contributes exactly one to `t`.

The current baseline-conditioned test uses raw baseline/selected counts. Supplying estimated controls does not by itself create corrected pseudo-counts that retain its conditional law. The proposed diagnostic should treat `t` as the sensitivity parameter for those counts; any corrected observation model requires its own derivation. Known correction, estimated correction and a sensitivity envelope are separate contracts.

An empirical confidence set for `t` must carry its coverage error into the study budget. With valid fixed-reference conditional tails and a valid bound set, a union-bound guarantee uses `alpha_test + beta_bound`; it is not automatically the old test's alpha. Independent calibration and freezing before endpoint unblinding protect the intended conditioning and prevent selection of the range or ordering from favorable endpoint results. A post-result frontier remains descriptive and is not a measured bound. The study's existing error allocation and stopping rule are not changed by this design note.

## Why classification needs a different boundary

With a general confusion matrix, observed category `j` has unnormalized mass `sum_i C_hc[j,i] r_hci p_i` (or `q_i` in baseline). That is a mixture of true routes. In general it cannot be written as a fixed routewise multiplier times `p_j` for all possible biological compositions. Calling the diagonal sensitivity of a classifier its recovery probability omits false positives entering from other routes. An effective multiplier obtained by dividing mixture mass by `p_j` depends on the unknown biological composition and does not become an independently measured recovery constant.

A shared confusion matrix is insufficient to preserve common curvature. Consider two contexts with uniform baseline `q=(1/3,1/3,1/3)`, biological selected distributions `p_1=q` and `p_2=(4/7,2/7,1/7)`. Both have biological `J=1`; the second is simply a different W/M tilt. All physical recovery probabilities are one. In every phase and context, classify half of true W outcomes as W and half as A, while A and M are always correctly labeled. With rows observed and columns true, the identical matrix is

```
C = ((1/2,0,0),
     (1/2,1,0),
     (0,0,1)).
```

The observed baseline is `(1/6,1/2,1/3)`. The second selected distribution becomes `(2/7,4/7,1/7)`. The observed baseline-adjusted `J` values are `1` and `16/9`, despite equal biological curvature and the same classification process throughout. Total callability is one for every true route; correct assignment probabilities are `(1/2,1,1)`. Both vectors are the same in each phase, so either mistakenly used as a diagonal recovery vector gives `t=1` and fails to describe the off-diagonal A entrants. Additional uniform callability of `3/5` leaves the normalized distributions unchanged. If a gold standard instead excludes the wrong-route calls, the retained baseline and selected context-two distributions become `(1/5,2/5,2/5)` and `(2/5,2/5,1/5)`, and the observed `J` returns to one, as the diagonal loss law predicts. These exact rational calculations are recorded in `CLASSIFICATION_COUNTEREXAMPLE.json`.

Diagonal loss plus adjudication that prevents wrong-route entrants admits the multiplicative recovery law. A frozen known permutation can be handled by relabeling the route registry. General misclassification, contamination, matrix-dependent thresholding, pooled amplification and composition-dependent detection require a richer observation law and its uncertainty. A special matrix may happen to preserve the contrast for a particular composition; that does not justify assuming a general preservation law.

## What the inspected sources actually supply

The cached version-one HiDenSeq main text was re-read directly and matched to the R32 provenance hash (`19e4953db7a99d5a17bd7ccfed55b4be97216902898e7a5553efe8e96aed04b2`; 523,750 saved provider-response bytes). Four relevant passages were verified in `CACHED_SOURCE_CHECK.json`:

* In the canUVanine comparison, its read-to-absolute-mutant scale is fitted in the non-UV arm and then transported to UV arms.
* The text reports corroboration by independent mutant colony counts before and after UV, with details assigned to supporting information that R32 did not acquire.
* Known-abundance barcoded spike-ins are proposed for future implementations; the passage is not a record that those standards were used.
* The discussion says other selective environments would require additional calibration.

Source: Husain et al., [A DNA-barcoded Luria–Delbrück assay resolves mechanisms of adaptation, v1](https://www.biorxiv.org/content/10.64898/2026.08.03.742544v1.full), DOI [10.64898/2026.08.03.742544](https://doi.org/10.64898/2026.08.03.742544), posted 7 August 2026. This is the same preprint evidence family already assessed in R32, not a new study, new acquisition or peer review. It supplies a useful calibration architecture but no native two-context W/A/M phase-specific recovery bound. A common scalar read-to-cell scale would cancel from the curvature even if perfectly known; route- and phase-dependent distortions are the relevant quantities here.

The inherited R12 source ledger for [DOI 10.1128/spectrum.03910-25](https://doi.org/10.1128/spectrum.03910-25) distinguishes bead-normalized cytometry, membrane-integrity gates and terminal CFU recovery. Its reported ratio of marginal CFU medians, 550, is not a recovery probability or a paired recovery ratio. Its declared raw supplement was unacquired, species identity was not systematic, and it supplies no route-phase-context denominator panel. The accompanying [DOI 10.1007/s00203-026-04995-3](https://doi.org/10.1007/s00203-026-04995-3) uses PA14/clinical isolate states, an approximate OD/CFU inoculum and technical flow events; these also do not identify the required native probabilities. The R12 ledger and reports were read here, but their original XML bodies were not present in the located cache and were not reauthenticated in this review. Preserve that inspection distinction.

The newly inspected [SLST-Seq study](https://doi.org/10.3389/fcimb.2026.1807759) provides a concrete calibration architecture: single-isolate DNA controls average 93% correct observed sequence assignment, a defined mixture underrepresents G1 (26.4% versus nominal 33.3%), and clinical samples receive pre-amplification before UMI labeling whereas SpikeMix controls bypass that stage. Pooled technical replicates do not provide independent introduced-cell recovery trials. These facts illustrate the classification/composition/transport distinctions; they identify no native recovery parameter. See `SLST_MEASUREMENT_NOTE.md` for the original assessment and `SLST_SOURCE_REVIEW.json` for eight verified main-text anchors and official-source provenance.

No inspected evidence supplies a numerical empirical `t` range, a known independent route-specific introduced denominator panel, a validated confusion matrix for the intended endpoint, or a native-control transfer envelope. Therefore this continuation can produce a conditional sensitivity diagnostic and a precise measurement request; it cannot select an evidence-backed robustness radius from these narratives. Firecrawl was not called because the parent reported zero remaining credits. No substitute broad search was made by this reviewer.

Original synthesis and illustrative counterexample: CC BY 4.0. Prepared with AI assistance; this is internal review, not qualified external biological review.
