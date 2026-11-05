# Independent finite-count review

The proposed `16*C` allocation is sufficient: each of two arms contributes
three observed-label upper limits, three correct-call-control lower limits,
one cohort gate-positive lower limit, and one known-Other false-gate upper
limit. Assigning each endpoint error `alpha/(16*C)` makes their joint coverage
at least `1-alpha` by the union bound. No independence between these endpoints,
arms, controls, or contexts is required. Each endpoint still needs its declared
fixed-denominator binomial marginal; stopping rules, cluster descendants, or
adaptive selection are not repaired by Bonferroni allocation.

On that event, `g >= Lg` and `f_native <= f_control <= Uf`, hence
`T >= max(0,(Lg-Uf)/(1-Uf))` when `Uf<1`, with bound zero at `Uf=1`.
Also `o_i <= Uo_i` and `d_native_i >= d_control_i >= Ld_i`. Combining gives
`p_i <= Uo_i/(beta*Ld_i)` when the denominator is positive. Monotonicity is in
the right directions: the eligibility bound increases with the gate lower
endpoint and decreases with the false-positive upper endpoint wherever the
positive branch applies. A separate positive-class gate sensitivity lower
bound is unnecessary for this argument.

Gate and route calls may use the same units. In particular, a gate exactly
equal to `label == W` gives perfectly dependent gate and W-label counts while
each remains binomial under independent identically distributed units.
The union-bound proof is unchanged. The confidence projection discards this
joint coupling, so it need not be sharp for the full observation model.

The prior engine's `certified_one_sided` passes `upper=True` to the preserved
binomial-tail routine for a lower confidence endpoint: the routine then
certifies the increasing tail `P_p(X >= k)` and moves the endpoint downward.
For an upper confidence endpoint it certifies `P_p(X <= k)` and moves upward.
Support endpoints and zero sample sizes yield 0/1 as required. Conversion of
the certified float to `Fraction.from_float` retains the exact certified
binary rational value. The source SHA-256 is checked before import; importing
the unchanged helper is therefore suitable for PR47. Hash validation protects
the preserved source identity, not native transport assumptions.

The scratch script independently summed exact rational binomial terms to
audit 182 endpoint checks, 1,066 one-sided coverage checks at probabilities
`j/40`, and 492 cases with perfectly dependent gate and W-label observations.
Every check passed. These finite checks support implementation behavior; the
general coverage claim follows from the binomial-tail construction and union
bound above.

Run `python3 audit_cp.py --repository /path/to/TMD --output receipt.json`.
Without `--repository`, the script searches its enclosing directories for the
installed repository. Outside a TMD checkout, `--repository` is required.
Without `--output`, it writes the receipt to standard output. It disables
bytecode writes and checks both pinned source hashes before importing either
repository module. Its only filesystem write is an explicitly requested output
receipt.

## Plug-in counterexample

Take `T=1/2`, eligible sensitivity `a=1`, false-positive rate `f=1/2`, giving
`g=3/4`. One native gate trial and one independent known-Other control trial
produce `(gate positive, control negative)` with probability `3/8`.
The empirical proportions are `g_hat=1`, `f_hat=0`, and their plug-in
eligibility bound is `beta_hat=1`, above the true `T=1/2`. Thus its error
probability already exceeds alpha `1/20`. For these same observations, with
`C=1` and tail `1/320`, exact one-sided CP endpoints are `Lg=1/320` and
`Uf=319/320` before outward rounding, so the valid conservative bound is zero.

Neither zero observed false positives nor a smoothed ratio establishes a
population false-positive bound of zero. With zero known-Other control trials,
the upper limit must be one and the resulting eligible-fraction bound zero.
