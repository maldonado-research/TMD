# Fixed-event ascertainment and sampling identities

## Frame and unit definitions

Condition on a finite catalogue E of distinct true mutation-birth events, known ancestry/carrier sets S_e and eligible terminal descendants indexed0..n-1. The catalogue and carrier mapping are supplied scientific assumptions, not outputs inferred by this package. Capturing a descendant means obtaining a validated true call for every target event it carries under this conditional model. Masks M range over all subsets of the eligible descendants, with a supplied normalized joint law Q(M).

Event inclusion is I_e(M)=1{M intersect S_e is nonempty}. The inclusion probability pi_e=sum_M Q(M)I_e(M) is dimensionless. Joint inclusion pi_ef=sum_M Q(M)I_e(M)I_f(M) is also dimensionless. The unweighted detected-event count D=sum_e I_e and weighted total T count distinct fixed events. In contrast, C=sum_e sum_{j in S_e}1{j in M} counts detected inherited event copies; a descendant carrying two distinct events contributes two target copies. C is not a cell count or a mutation-birth count.

A known empty S_e can represent an extinct or otherwise unobservable event and has pi_e=0. Unknown membership is different: it is refused, not represented by an empty set. Even a perfect terminal call law cannot restore an event with no eligible terminal descendant. Unknown, never-catalogued events remain outside the supplied finite frame.

## Sharp union bounds and constructions

Write A_j={j in M}. For any j in S_e, A_j is contained in the event's inclusion union, so pi_e>=max p_j. The indicator of a union is at most the sum of its component indicators, giving pi_e<=sum p_j, and every probability is at most1.

Both endpoints are attainable for arbitrary specified marginal probabilities. For the lower endpoint, take one shared uniform variable U on[0,1] and set A_j=[0,p_j). These events are nested, so their union has length max p_j. For the upper endpoint, arrange successive intervals of lengths p_j along a unit circle. If total length is at most1, the intervals are disjoint and their union has that total length. If the total exceeds1, their concatenation covers the circle and the union has length1. Each wrapped interval still has its specified marginal length. Subdividing at rational endpoints produces the implementation's finite rational mask laws. Empty marginal lists give the degenerate zero-union law.

Under explicit joint independence only, Pr(no A_j)=product_j(1-p_j). Without independence the Fréchet interval remains. A single known cell-call marginal cannot reveal correlations induced by clone viability, shared processing, batch failure, joint calling, family-specific recovery or operator selection.

## Event joint inclusion

An event may have many descendants, and different events may share carriers. For independent descendant calls, inclusion-exclusion yields

    pi_ef=1-product_{j in S_e}(1-p_j)-product_{j in S_f}(1-p_j)
             +product_{j in S_e union S_f}(1-p_j).

If carrier sets are disjoint, this reduces to pi_e*pi_f under independent descendant calls. If carrier sets overlap, event inclusions can remain dependent even in that independent-descendant model. General complete mask laws need no product assumption: direct sums determine the joint inclusion probabilities. A compatible pair probability lies between max(0,pi_e+pi_f-1) and min(pi_e,pi_f).

## Classical fixed-catalogue Horvitz–Thompson calculation

Assume pi_e>0 for every e in the fixed target catalogue. By linearity,

    E_Q[T]=sum_e E_Q[I_e]/pi_e=sum_e1=|E|.

No independence is required. Cov(I_e,I_f)=pi_ef-pi_e*pi_f, so bilinearity of covariance gives the stated exact double-sum variance. Its diagonal term is1/pi_e-1; its off-diagonal terms can be positive or negative. Full finite mask enumeration independently computes E_Q[T] and E_Q[(T-E_Q[T])^2] in the synthetic verifier.

An observed HT value may exceed the fixed catalogue size and need not be an integer. Unbiasedness is a design expectation, not exact reconstruction in each observation. Variance may be large when inclusion is rare or jointly correlated. Knowing only pi_e does not determine the variance; pi_ef is also needed. No estimated-pi adjustment, empirically estimated variance, confidence interval or biological mutation likelihood is implemented.

For pi_e=0 the term I_e/pi_e is undefined and that event cannot be recovered by this estimator. The code therefore refuses the complete-catalogue total if any event has zero inclusion. Estimating the positive-inclusion subcatalogue would target a different total and leave invisible-event abundance unresolved. A known empty catalogue has total zero. These statements do not infer that a biological experiment has no unobserved events.

## Conditions biological data would still need

- A fixed event definition, ancestry evidence and mutation-origin mapping must separate one birth inherited into many cells, distinct recurrent births, standing variation and additional genetic acquisitions. A catalogue inferred only from surviving genomes may omit extinct events and bias carriers.
- The eligible terminal unit and true-call criterion must be justified. Cell isolation, outgrowth, sequencing and correct genotype calling are separate stages. Real locus-specific errors may need event-specific call indicators and a richer joint law; false positives cannot be represented as true calls from absent carriers.
- The any-eligible-descendant OR rule must match the assay. Multiple-support branch callers, pooled tissues, copy-number changes and ancestry uncertainty can defeat this simplification. The supplied ancestry flag is not an experimental check.
- Validated descendant marginals and their dependence need independent measurement in the actual background and context. Similar realized stage fractions or growth distributions do not establish a homogeneous common law. Observing a mask zero times in a finite sample does not establish zero population probability.
- Positive HT inclusion and known design probabilities do not calibrate an existing TMD confidence engine, supply relative mutation generation, justify Poisson counts or identify a full biological birth catalogue. If event counts and ancestry are themselves random, a separate mutation/lineage process must be specified rather than silently averaging this fixed-catalogue calculation into a biological claim.
- Generic route inclusion differences can distort detected-event shares. Route ordering, supply, growth/loss, capture and held-out nuisance parameters still need the pre-outcome biological contract. The synthetic route example proves only a finite expected-count observation identity.

This extension uses established indicator algebra, sharp Fréchet union bounds and Horvitz–Thompson sampling. It adds reproducible conditional project mathematics, not a new theorem or causal force. No biological study, intervention, clinical benefit or external qualified review was performed. All previous TMD hypotheses, actual-study fields, count-law requirements, simultaneous error budgets and fixed stopping rules are preserved.

## Established method and inspection depth

Horvitz, D. G. and Thompson, D. J. (1952), “A Generalization of Sampling Without Replacement from a Finite Universe,” *Journal of the American Statistical Association* **47**(260), 663–685. DOI: [10.1080/01621459.1952.10483446](https://doi.org/10.1080/01621459.1952.10483446). The parent review checked Crossref bibliographic metadata only: response 3,164 bytes, SHA-256 `51b215f6a341dc6c8356c3acc38b5a69a3ba139f9948a60afcd45f23d723827f`. No primary full text was acquired or inspected for this candidate. The exact covariance derivation above is supplied directly and is not a mutation-process likelihood or biological validation. The R000020 producer made zero network requests.
