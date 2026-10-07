# Conditional capture derivation and interpretation

## Sampling units and intensity

Let N~Poisson(m) count model precursor events in a specified frame, and J_r be iid terminal eligible-unit marks independent of N. The total terminal count is R=sum_{r=1}^N J_r. A mark may describe an event's descendants, survivors or recoverable units at a declared endpoint. Calling m an intensity does not authenticate molecular mutation events. m has units expected precursor events per complete specified frame; pi and c are dimensionless, and nu_l is expected captured l-unit event marks per frame. b=sum nu_l has units detected nonempty event marks per frame. The mean sum l*nu_l has units detected observation units per frame. A probability such as Pr(X=0) is dimensionless; -log of this probability is numerically an intensity for that one frame.

Under conditional independent homogeneous unit capture at c, the captured event mark L|J=j is Binomial(j,c). If g(u)=sum pi_j u^j, the observed PGF is

    F(z)=exp{m[g(1-c+cz)-1]}.

Rewrite its exponent as sum_{l=1}^B nu_l(z^l-1). Expansion yields the forward binomial matrix stated in the README. Its diagonal entries c^j are positive when c>0, so its positive-support block is invertible. Back-substitution identifies w_j=m*pi_j for j>=1. Equivalently,

    w_j = sum_{l=j}^B binom(l,j) nu_l [-(1-c)]^(l-j)/c^l.

This closed form exposes alternating signs and small-c sensitivity. Exact arithmetic is appropriate for checking algebra, while empirical inference needs a justified likelihood, calibration uncertainty and an explicit statistical analysis. The present code does not supply those.

When pi_0=0, m=sum_{j>=1}w_j. If pi_0 may be positive, the same inverse identifies only m_+=m*(1-pi_0). Every nonnegative invisible weight w_0 can be added without affecting F. One may set m=m_++w_0 and pi_j=w_j/m, pi_0=w_0/m for m>0. At c=1 this ambiguity remains; perfect terminal recovery cannot retrospectively observe absent terminal units. In the zero-intensity boundary all w_j are zero and the positive mark law is undefined.

The singleton example shows a different ambiguity: F(z)=exp[m*c*(z-1)] when J=1. Unknown capture leaves the product m*c. This is a complete-law equivalence within a strictly positive finite family; it does not depend on comparing only moments or zero fractions.

## Population law versus sampled counts

Within the finite compatible compound-Poisson family, the complete population PGF supplies its log coefficients and thereby its positive jump intensities. A finite collection of culture counts is an empirical sample, not those coefficients. A truncated observed count table is not complete F, and a finite support bound on each latent J does not make aggregate X finite. Finite mixtures, culture-specific random parameters, non-Poisson precursors and correlated recovery can require different models. No extraction algorithm, model-selection rule or empirical inference is registered here.

The inverse's rejection of a negative weight applies to exact inputs interpreted as a complete population vector at a fixed c and B. Negative estimated coefficients could reflect noise, calibration error, a wrong bound, model mismatch or numerical instability. They are not by themselves a cancer, mutation or lineage-origin finding.

## Sharp bounds from the void exponent

For positive J, a_j(c)=1-(1-c)^j lies between c and a_B(c). Thus

    b=m*E[a_J(c)] lies between m*c and m*a_B(c).

Solving gives the stated point bounds. Fixed J=B and J=1 attain the respective endpoints. If B>1 and c<1, mixtures of J=1 and J=B span every mean capture between c and a_B(c), so every intervening m is feasible for that b. If B=1 or c=1, the bounds collapse. For b=0 and c>0, m=0 within the positive-mark model.

Without finite B, a_j(c)<=1 still gives m>=b, and a_j(c)>=c gives m<=b/c. For c<1,b>0, finite positive J always gives a_J(c)<1, so m>b; unboundedly large fixed J approach the lower endpoint. These zero-only bounds do not identify a mark distribution, even when they identify m at c=1.

For a deterministic rectangle, a_B(c) increases with c. Jointly selecting b_L,c_U,J=B minimizes m, while b_U,c_L,J=1 maximizes it. This establishes the stated [b_L/a_B(c_U),b_U/c_L] envelope when those endpoint combinations are admissible. The rectangle assumes the externally justified allowed set actually includes every combination; narrower dependence restrictions can sharpen it. It has no statistical coverage without separately justified simultaneous coverage for b and c. Such a procedure would have to account for its uncertainty within the existing project error budget; none is added here.

## Measurements still required

- The frame and independently founded culture denominator must be declared. Technical plates and confirmations do not multiply founder counts.
- The captured unit must be authenticated. One CFU packet can contain multiple cells; the same count law might describe packets rather than single cells. The coefficient inverse cannot label its own units.
- Homogeneous independent c must be justified for the actual eligible units, context and assay. Nominal plated volume is not by itself capture, viable recovery, correct classification or transport calibration. Route-specific or clone-specific capture, clumping and nonlinear detection defeat this simple matrix unless a new explicit observation law is justified.
- Positive J cannot be inferred from a passing split check. Extinction, post-event loss or assay ineligibility can yield zero terminal marks. Counting such events requires lineage/origin information outside the terminal observation law.
- New mutation, standing variation and imported alleles remain distinct origins. Biological division exposure, timing, growth, inheritance, selection, drift, survival and establishment need independent justification before m or m_+ can be related to a mutation probability per division.
- A reporter's measured capture and retention do not automatically transfer to native Wsp/Aws/Mws routes or to cancer cells. No such transfer is assumed.

This conditional extension uses standard generating functions, binomial inversion and Poisson marking. It does not change TMD's operational natural-dominance definition, shared-curvature restrictions, actual-study registry, prospective forecasts, confirmatory denominator laws, error allocations or stopping rules. No biological experiment, rate fit, treatment claim or new theorem is reported.
