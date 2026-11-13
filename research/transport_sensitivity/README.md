# Transport sensitivity after methods 0.7.0

Prepared 13 November 2026 UTC, with AI assistance and independent internal computational review.

The integrated 0.7.0 calculation assumes that source controls transfer conservatively to the native assay. This addendum makes departures from that premise explicit. It propagates external probability deficits through the existing outer bounds and measures when a *saved synthetic example* loses its rejection of common curvature. It supplies no native transport measurements, new theorem, mathematical priority, biological validation, or study recommendation.

[Published 0.7.0 method](../integrated_inference/README.md) · [Independent review](INDEPENDENT_REVIEW.md) · [Bounded source assessment](SOURCE_ASSESSMENT.md)

## External envelopes and the inherited event

For each independently trained, frozen pipeline require, at every possible learned threshold t,

    f_native,H(t) <= f_control,H(t) + delta_F.

For each true route i and the realized complete gate-and-label pipeline require

    d_native,i(D) >= d_control,i(D) - delta_i.

H denotes prior training; D includes all training and calibration data across the whole context/arm family. Future count marginals must still be valid conditional on D, as in 0.7.0. A control transfer inequality merely averaged over training is insufficient. A correct-call probability among gate survivors is a different target from the full known-route denominator required here.

On the *same* simultaneous calibration/count event used by 0.7.0, let F be its source-Other upper bound, L_i its source correct-call lower bounds, gL its full-cohort gate lower bound, and U_i its observed-label upper bounds. Define

    F*    = min(1, F + delta_F)
    L_i*  = max(0, L_i - delta_i)
    beta* = max(0, (gL-F*)/(1-F*)) if F*<1; otherwise 0
    u_i*  = min(1, U_i/(beta*L_i*)) if beta*L_i*>0; otherwise 1.

The gate mixture implies T>=beta*. Nonnegative classifier contributions imply o_i >= T*p_i*d_native,i >= beta*L_i* p_i. Thus the true eligible composition obeys p_i<=u_i*. Apply the unchanged capped-simplex Q=p_A^2/(p_W*p_M) and context J=Q_selected/Q_baseline projections.

These are standard bound-propagation and mixture arguments. They preserve the inherited level-alpha common-J guarantee only under the stated deterministic transport envelopes and all original premises. The new program does not recalculate CP endpoints, establish joint endpoint coverage, or verify the scientific premises. Its alpha field records the input bundle's declaration; that field does not certify confidence coverage.

One inherited event supports every displayed deterministic scenario whose transport envelope actually holds. A descriptive sensitivity grid therefore needs no new multiplicity allocation. It cannot establish that any displayed deficit is biologically admissible. If deficits are estimated using random external confidence bounds with joint noncoverage gamma, a union argument gives at best 1-alpha-gamma coverage unless the budget is redesigned. Data reuse, adaptive validation or stopping need their own argument.

## Nesting, decision policy and a declared path

Increasing deficits increases F*, decreases beta* and L_i*, and increases the caps. Positive capped-simplex sets and their Q/J ranges expand. Starting with evaluable arms, common-J rejection can disappear but cannot return along a coordinatewise increasing path.

The reported boolean is not globally monotone from an *unevaluable* starting point. An empty cap set may become nonempty and reveal separating intervals. For example, use baseline caps (1/3,1/3,1/3) in both contexts, first-selected caps (1/4,1/2,1/4), and second-selected caps initially (1/2,1/4,1/8). The last set is empty. Raising its M cap to 1/4 makes it a singleton with Q=1/2, while the first context has J=4. The now-evaluable calculation rejects. Incompatibility is not acceptance or a curvature rejection.

The supplied bisection refuses an unevaluable starting design and searches only from an evaluable, rejecting start. A scalar frontier requires a declared path through the multidimensional deficits. Three paths apply a common t to: both deficits; false passing alone; or correct calling alone. The prototype uses one common false-pass deficit and one common correct-call deficit across all arms/routes. The formulas above also describe heterogeneous externally justified deficits, which this interface does not expose.

## Exact results for the saved synthetic fixture

The input bundle is an exact transcription of the certified endpoints in the pinned 0.7.0 strict-separation fixture, not new count or calibration data. Every decision uses BigInt fractions. Decimal displays do not decide rejection.

| Common path | Still rejects at | Compatible at | Approximate first-loss interval |
| --- | --- | --- | --- |
| Both deficits t | 746603/16777216 | 746604/16777216 | [0.044501006603241, 0.044501066207886] |
| False-pass deficit t only | 6764835/16777216 | 6764836/16777216 | [0.403215587139130, 0.403215646743774] |
| Correct-call deficit t only | 798621/16777216 | 798622/16777216 | [0.047601521015167, 0.047601580619812] |

Each exact bracket has width 2^-24. These brackets locate loss of rejection by this conservative outer projection. They do not locate an actual biological error rate, a sharp joint-feasibility frontier or a power threshold. Equality of finite positive interval endpoints counts as compatibility.

In the common-deficit path, a deficit of 0.05 means five *percentage points* of additional native false passing and five percentage points of reduced native correct calling, not a relative five-percent change. At t=0, the common lower/upper candidates are approximately 7.44956 and 1.21432, hence separated. At t=0.05 they are 3.54265 and 4.72526, hence overlap. At t=0.15 the outer common interval is (0,infinity). Overlap does not establish full joint feasibility or equal biological curvature.

A hand-checkable population example has F=1/5, gL=4/5, beta=3/4, all L_i=4/5, and U=(3/20,3/10,3/20). With a common correct-call deficit delta and no false-pass deficit, z=beta(L-delta)=3/5-3delta/4. For z>3/10, Q_min=(20z-6)^2/9. At delta=0, Q=4. At delta=1/5, caps are (1/3,2/3,1/3) and uniform composition attains Q=1. A fixed exact comparator Q=1 then touches the interval. This is deterministic population arithmetic, not another confidence or count calculation.

## Why source controls and unlabeled native observations cannot validate transfer

Consider source Other scores always zero, and source route controls that always pass and are called correctly. The learned strict gate is score>0.

In native world A, let T=1/2, eligible composition uniform, eligible calls perfect and Other units fail the gate. The observed W/A/M probabilities are each 1/6 and U is 1/2.

In world B, choose any positive eligible composition and any T strictly between zero and one. For every true class, including Other, generate W/A/M each with probability 1/6 and U with probability 1/2, independently of truth. Set score one for called labels and zero for U. All source-control and native observable score/gate/label laws match world A, but the native false-pass probability is 1/2 and each true-route correct-call probability is 1/6. T and the eligible composition may vary without changing those observations; Q can take any positive value.

Thus unlimited observations of those unlabeled marginals cannot generally identify the required deficits. Truth-bearing native validation or additional justified structural restrictions are needed. Observations can contradict an assumed model; compatibility cannot authenticate its transport assumptions.

Even training-averaged tail dominance is insufficient for a learned gate. Let independent training H be 0 or 2 equiprobably. Every calibration score equals H, so M=H and the true control tail at M is zero. Let native score be 1 for H=0 and -1 for H=2. Averaged over H, native {-1,1}/2 is stochastically dominated by control {0,2}/2 at every fixed threshold. Yet native passing at learned M is one in the first training state and zero in the second. Any strict certificate F<1 fails as a native bound half the time. This example can be realized by fixed raw control/native inputs and a training-indexed score map; it does not require using calibration observations for training.

## Reproduce and interpret the checks

The original JavaScript core and verifier were executed in the available V8 tool runtime. Python, CP inversion and the filesystem/Node CLI wrappers were not executed because the selected execution environment failed. Node commands below are reproduction instructions; this turn did not run those commands.

From the repository root with Node 18+:

    node - <<'JS'
    const fs = require("node:fs");
    const api = require("./research/transport_sensitivity/transport_sensitivity.cjs");
    const verify = require("./research/transport_sensitivity/verify_transport.cjs");
    const input = JSON.parse(fs.readFileSync("research/transport_sensitivity/example_saved_endpoints.json", "utf8"));
    const saved = JSON.parse(fs.readFileSync("research/integrated_inference/example_strict_separation_result.json", "utf8"));
    console.log(JSON.stringify(verify.runTransportChecks(api, input, saved), null, 2));
    JS

The independent diagnostic also accepts that pinned saved fixture:

    node research/transport_sensitivity/INDEPENDENT_EXACT_ORACLE.mjs \
      research/integrated_inference/example_strict_separation_result.json

The parent verifier passed 12,344 assertions, including 30 zero-deficit endpoint comparisons, 771 scenarios, 9,216 cap-nesting comparisons, 2,304 common-interval/decision comparisons, 16 refusals and seven hand/boundary checks. The separately written oracle passed 106 stored-field comparisons, 68,988 invariant assertions and six direct polynomial endpoint checks. The parent replayed that independent core and cross-compared 465 scenario fields. These bounded checks support the implementation; the general coverage statement rests on the conditional argument above.

[Verification receipt](VERIFICATION.json) · [Exact scenarios and frontier endpoints](example_sensitivity_result.json) · [Independent receipt](INDEPENDENT_EXACT_RECEIPT.json) · [Provenance](PROVENANCE.json)

The independent receipt's transfer-blob wording records the agent's intermediate handoff stage, before parent integration. A source Git blob identifier binds bytes at its cited commit; it does not establish prospective registration, source-truth or native transport.

All 26 actual study inputs and 18 planning fields remain unresolved. This is an additional sensitivity diagnostic, not a change to the protected registry, frozen forecast comparison, study error allocation or stopping rule. The published 0.7.0 archive remains unchanged. This bounded GitHub addendum does not require another Zenodo release.

Original code is MIT and original documentation CC BY 4.0 under repository terms. Source publications retain their own rights; no third-party article body, data archive, individual human metadata or private handoff is bundled.
