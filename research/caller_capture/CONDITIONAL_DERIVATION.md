# Finite support/reference probabilities and sharp bounds

## Units and observation frame

Condition on one specified true event, known eligible descendants, disjoint known carrier/reference sets C,R and a correct target-call mask M. A mask bit represents a validated correct alternate call in C or validated correct reference call in R. It is not a mutation birth, an independent cell trial, a sequencing read or merely a cell-isolation success.

The partial inclusion indicator is f(M)=1{|M intersect C|>=k and |M intersect R|>=r}. Its probability is pi=sum_M Q(M)f(M), with Q a supplied complete joint population/design law. Expected carrier-copy calls sum_j in C p_j; expected reference calls sum_j in R p_j. Neither equals pi or counts new mutations in every descendant. A zero threshold-support predicate is structurally unobservable regardless of the true event's presence. A known empty carrier set is allowed; unknown carriers are refused.

## The independence special case

Under explicitly justified joint independent correct calls, carrier and reference groups are disjoint functions of independent coordinates, so

    pi = Pr(sum_{j in C} Bernoulli(p_j) >= k)
           * Pr(sum_{j in R} Bernoulli(p_j) >= r).

These tail probabilities are finite Poisson-binomial probabilities, not an admitted biological count law. The implementation directly enumerates the independent mask law. For two half-probability carriers and one half-probability reference, k=2,r=1 gives (1/4)(1/2)=1/8. This product is invalid under a general joint law.

Keeping the carrier pair's complete common-success/failure law fixed, both are correct-called with probability 1/2. The reference marginal 1/2 alone permits it to occur exactly with the pair or exactly when the pair is absent. The event probability is respectively 1/2 or zero. Independent reference calling gives 1/4. Thus measuring the carrier joint law and reference marginal still leaves a reference-dependence requirement.

## Marginal-only finite linear program

For n eligible descendants, assign nonnegative probabilities w_M to all 2^n masks. The constraints are

    sum_M w_M = 1,
    sum_{M containing j} w_M = p_j for each j.

Write A for the (n+1)-by-2^n binary matrix with a first row of ones and subsequent mask-bit rows, and b=(1,p_0,...,p_{n-1}). The lower and upper event probabilities minimize/maximize the linear objective sum_M f(M)w_M subject to Aw=b,w>=0.

For admitted p in [0,1]^n, the independent product law is one feasible point. The feasible set is a closed bounded subset of a simplex, so both objective extrema are attained. The columns for the zero mask and singleton masks show that A has full row rank n+1.

A vertex cannot have more than n+1 linearly independent positive-support columns. If its positive columns were dependent, a nonzero null direction could perturb those positive weights in both directions by sufficiently small amounts while preserving Aw=b and nonnegativity, contradicting extremality. Every vertex's independent positive support can be extended to an n+1-column basis because A has full row rank. Solving that basis gives the same vertex, with extra basis weights zero. Conversely every nonnegative basic solution is feasible. Enumerating all nonsingular bases therefore includes every extremizing vertex, even degeneracies and repeated representations.

For n<=4, at most choose(16,5)=4,368 candidate bases are examined. Rational matrix inversion is performed on small structural binary matrices. Each inverse is stored with a common integer denominator; supplied rational b is likewise expressed over a common denominator. Candidate weight nonnegativity and objective comparisons then use integer arithmetic without uncertified floating point. The final lower/upper values and witness weights are exact Fractions. Cache reuse changes runtime, not the feasible set.

The witness laws prove attainability. The complete basis argument supplies the opposite inequality: an unexamined compatible probability law cannot improve an objective beyond the enumerated extreme vertices. This is established finite-polytope/linear-program reasoning; no mathematical priority claim is made.

## Concrete boundaries

For conjunction of all three half-probability calls, the classical bounds are max(0,sum p-2)=0 and min p=1/2. The lower law can place calls on configurations that never contain all three; the upper law has all-three success or all-three failure with equal mass.

For at least two of three half-probability carrier calls, if pi is the inclusion probability and S the number of calls, E[S]=3/2. Outside the predicate S<=1 and inside S<=3, giving E[S]<=1+2*pi and pi>=1/4. Inside the predicate S>=2, giving E[S]>=2*pi and pi<=3/4. Laws on singletons plus the all-three mask, or on pair masks plus the empty mask, attain the bounds. The benchmark's LP witnesses independently replay these identities.

A four-bit predicate requiring at least one carrier call from {0,1} and one reference call from {2,3}, with all marginals 1/2, ranges from zero to one. A law alternating full carrier calls and full reference calls attains zero; pairing one carrier with one reference attains one. The independent value 9/16 is only one compatible choice.

## Retained scientific limitations

The complete mask law and the marginals are conditional assumptions, not recovered from nominal stage fractions, internally estimated consensus sensitivity or unobserved empirical masks. No inclusion probability, mutation rate, confidence interval, statistical rejection, general power or full count likelihood is fitted to biology.

The monotone support component does not authenticate the designated truth frame. Real origin calling can require ancestral alleles, opportunity/copy state, scores, lineage consistency, absence of parallel acquisition, episode definitions, post-expansion exclusion and more than one target-specific observation state. Incongruent additional observations can defeat a native call even where this partial predicate passes. False-positive calls from noncarriers are not correct-call mask successes and require a richer validated observation model.

Independent founders, division/time exposure, mutation production, inheritance, growth, loss, sampling, genotype recovery and first successful arrival remain separate. Neither sharpness of a conditional bound nor an endpoint witness identifies extinct or never-catalogued events. This extension changes no actual study registry, TMD forecast, count-law admission, error allocation or stopping plan. It prepares a precise measurement question for qualified review; it does not perform that review or validate a biological hypothesis.
