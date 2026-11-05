# Finite synthetic operating characteristics of the frozen route forecasts

Ricardo Maldonado · 5 November 2026 · Original design analysis with AI assistance

This original design diagnostic repeats the existing forecast builder and certified score procedure through **2,560 entirely synthetic studies**. It exposes a practical distinction: a common-curvature predictor can clearly outperform the supply–establishment predictor while rarely clearing a gate that also requires superiority to the flexible predictor. The latter shares its population forecast under common curvature. The calculation supplies no biological observations, achieved biological power, scientific sample size, registry values or causal result.

The code reads `research/prospective_design/verify_design.py` and `research/certified_score/certified_score.py` unchanged. It hashes those files and `REGISTRY_CANDIDATE.json` before and after execution. The illustrative simulation settings do not replace any unresolved study allocation, threshold, comparator, stopping rule or forecast algorithm. Established count models, Clopper–Pearson intervals, linear score projection and Monte Carlo evaluation are used without a new-theorem claim.

## What is repeated

There are five prespecified laws, two calibration budgets, two endpoint budgets and 128 repetitions per combination. Four complete training contexts have underlying `exp(x)=(1/2,4/5,5/4,2)`; two held-out contexts have underlying `exp(x)=1`. Contexts are fixed before all draws. No context screening or adaptive selection stage is performed.

Each repetition independently generates baseline counts, baseline/selected recovery controls, establishment controls, training endpoints and held-out endpoints. Each baseline count vector has either 30 or 300 observations; each binary control arm has that same chosen denominator. Every training context has a fixed full frame of 320 endpoint units. Each held-out context has a fixed full frame of either 80 or 400 units. These are arbitrary bounded design examples, not recommended experimental sizes.

The baseline law is uniform. Binary recovery controls have probability `3/4` in every route and phase. With `r=exp(x)`, establishment probabilities are `(r/4,F_A,1/(4r))`. Conventional endpoint truths normalize these underlying probabilities, independently of their noisy control estimates. Common-curvature endpoint truths normalize `(r,exp(theta),1/r)`, with `exp(theta)=3/2` or `3`.

| Synthetic law | Training `F_A` | Held-out `F_A` | Qualifying endpoint truth |
| --- | --- | --- | --- |
| Conventional equal | `(1/4,1/4,1/4,1/4)` | `(1/4,1/4)` | normalize `F` |
| Conventional weak contrast | `(9/40,11/40,11/40,9/40)` | `(9/40,11/40)` | normalize `F` |
| Conventional strong contrast | `(1/10,3/10,1/2,4/5)` | `(1/10,4/5)` | normalize `F` |
| Common weak curvature | `(1/10,3/10,1/2,4/5)` | `(1/10,4/5)` | normalize `(r,3/2,1/r)` |
| Common strong curvature | `(1/10,3/10,1/2,4/5)` | `(1/10,4/5)` | normalize `(r,3,1/r)` |

Each full endpoint frame is IID categorical with qualifying probability `4/5`. The four other probabilities are Other `1/10`, no-qualified-outcome `1/20`, unresolved-classification `1/40`, and missing `1/40`. Their counts remain in the ledger. Conditional W/A/M counts therefore have the stipulated multinomial law given their qualifying total. Recovery controls and endpoint qualification are **separately stipulated operational laws**, not an absolute biological recovery map. The simulation does not establish their biological transfer or any source-specific generative model.

The unchanged builder fits the restricted predictor and all three existing comparators using the simulated training and independent control records. Its output floats are normalized as exact rational representations, then rounded by largest remainder to positive vectors with denominator `2^40`. Those rational vectors are the forecasts actually frozen and scored; the numerical certificate does not identify them with ideal real-number regression/exponential outputs. Every plan is hashed before the held-out draws.

The unchanged exact score engine uses an illustrative standalone alpha `1/20`, equal context weights, 24 CP bisection bits, 24 log-series terms, 56 log fraction bits and 48 report bits. Success requires every comparison's lower endpoint to exceed zero; failure requires at least one upper endpoint below zero. All remaining studies are inconclusive. The zero gates are synthetic choices, not biological success criteria. No comparator is removed. Zero-qualifying studies are retained as unevaluable in simulation denominators; none occurred in the 2,560 main repetitions.

## Observed synthetic results

The table selects the larger calibration and endpoint cells: 300 observations per baseline/control arm and 400 full-frame held-out units per context. Every row contains 128 independently repeated studies; qualifying totals remain random.

| Law | All-comparator success | Failure | Inconclusive | Positive certificate versus `q*F` | Positive certificate versus flexible |
| --- | ---: | ---: | ---: | ---: | ---: |
| Conventional equal | 0 | 6 | 122 | 1 | 2 |
| Conventional weak contrast | 0 | 6 | 122 | 0 | 3 |
| Conventional strong contrast | 0 | 121 | 7 | 0 | 53 |
| Common weak curvature | 1 | 3 | 124 | 122 | 2 |
| Common strong curvature | 4 | 4 | 120 | 128 | 4 |

In the last row, mean realized true gains were approximately `0.149082` nats against supply alone, `0.234184` against supply–establishment, and `0.0000724564` against flexible. Positive score certificates occurred 122, 128 and 4 times respectively. The all-comparator success fraction was `4/128=3.125%`, with marginal 95% Monte Carlo CP interval approximately `[0.858%,7.808%]`. This is a synthetic frequency under this finite training and calibration scheme. It is not the power of an admitted biological study or a guarantee across other laws.

The conventional-equal label describes its underlying law; noisy fitted algorithms need not have equal realized expected scores. A success or failure is checked against the actual independently frozen predictors, not against a label assigned to the generating family. Common-curvature truth therefore also need not yield success for every realized training sample.

No false score certificate was found when checking all decisions against exact enclosures of their replicate-specific true expected gains. No truth classification remained numerically ambiguous. The simultaneous outcome region missed a generating truth in 80 of 2,560 repetitions. These are finite computational observations, not proofs of a zero error rate or the general coverage guarantee. Each reported Monte Carlo interval is marginal; the many intervals are not simultaneous. For 0 events in 128 repetitions its two-sided 95% upper bound is about 2.84%, not zero. The general score guarantee remains the existing engine's conditional sampling argument.

## Why the flexible comparator matters

Linearity of the same ridge fit gives

```text
theta_flexible(x) = mean(theta_training) + b_theta * (x - mean(x_training))
eta_flexible(x) = eta_restricted(x).
```

The synthetic held-out feature is centered on the underlying training feature mean. At an exactly realized feature mean the two ideal predictors coincide; calibration noise makes the realized features differ. Under correctly specified common curvature and increasing independent information, the flexible curvature slope also approaches zero, so both predictors approach the same population forecast even away from that center. A finite restricted advantage then reflects estimation variance, rather than separation of the two population probability laws. More held-out endpoints cannot create a positive expected margin absent from the frozen forecasts. An inconclusive score comparison here is not evidence against common curvature or a statement about biology.

An additional check uses forecasts alone, before endpoints. For a comparator `m`, every possible conditional endpoint law obeys

```text
Delta_m <= sum_c w_c max_i log(pi_restricted,ci / pi_m,ci).
```

The script bounds the right side using certified upper log endpoints. If any comparator's bound is at most a proposed strict margin, the all-comparator margin is unattainable for those frozen predictions, regardless of endpoint count. This is the elementary maximum of a linear score over a simplex; it is not a new statistical test or a new theorem.

The separately implemented `feasibility_ceiling.py` accepts an existing plan or complete score-input document and reports this necessary condition without using outcome counts. From the repository root, run `python -B research/operating_characteristics/feasibility_ceiling.py /path/to/score-input.json`. Passing the ceiling check does not establish joint feasibility or statistical power.

Margins `0.01` and `0.05` nats are reported only as illustrative pre-outcome diagnostics; the executed score gate remains zero. In the common-strong, calibration-300, endpoint-400 cell, strict all-comparator gain above `0.05` was impossible from the frozen vectors in 127/128 repetitions; gain above `0.01` was impossible in 107/128. The common-weak counterpart had the `0.05` impossibility certificate in 128/128 repetitions. These finite counts establish neither universal impossibility nor a scientific choice of margin.

## What this supports next

A successor planning exercise should first distinguish three scientific targets: adequacy of a common-curvature restriction, finite-training predictive advantage over specified algorithms, and a causal mechanism. The present frozen score comparison addresses the second target under its operational sampling assumptions. Fixed positive-margin superiority to a flexible model that converges to the same forecast is not a consistent test for the presence of common curvature. It cannot identify a special mechanism.

Before collecting data, an authenticated study would still need admitted measurement and transfer assumptions, target contexts, meaningful thresholds, budgets, fixed stopping and independent design review. A sensitivity design could prespecify held-out features away from the training center or vary training information as well as calibration precision, but those studies have not been run here. The current comparators, thresholds, registry and methods remain unchanged; no favorable gate is selected retrospectively from these results.

## Reproduction and artifacts

Run the standard-library-only script from an existing TMD checkout, with an output directory outside it:

```sh
python -B research/operating_characteristics/operating_characteristics.py \
  --repo . --replicates 128 --seed 20261105 \
  --output /tmp/tmd-operating-results.json
```

The script emits every repetition's summaries and decisions, exact representative input/result documents for the first repetition of each cell, source hashes, the explicit configuration and deterministic full JSON. Wall-clock progress is printed but omitted from saved results. `SUMMARY.json` retains all 20 cell settings and summaries together with the full result's SHA-256, byte size and script/source hashes. The full per-repetition file can be regenerated outside the repository.

The [independent review](INDEPENDENT_REVIEW.md) checked the rational generating laws, all three expected-gain bounds in a sampled study against 90-digit arithmetic, the forecast-only ceilings, and six tiny-count repetitions including two unevaluable endpoint cases. This is internal computational review, not external peer review, biological replication or study registration.

The [recent-source screen](RECENT_SOURCES.md) records separately inspected abstract-level leads. It supplies no new native measurement panel.
