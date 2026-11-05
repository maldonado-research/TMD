# Independent classification-bound assessment

Prepared 5 November 2026 as internal mathematical and software review. All examples
are synthetic. This review inspected the existing conditional-recovery classifier
counterexample, prospective observation contract, and preserved certified
Clopper–Pearson implementation. It supplies no biological calibration or external
peer review.

The claimed population identification set is correct under its stated narrow
model: every cohort member has one of three true routes W/A/M, every member
contributes one observed W/A/M/U label, and each arm/context may have its own
arbitrary column-stochastic classifier with diagonal **lower bounds** d_i.
Observed probabilities o include U in their common denominator. Necessity is
o_i >= d_i p_i. For sufficiency, let z_i=o_i-d_i p_i for W/A/M, z_U=o_U,
and R=sum z. If R>0, set C_ji=d_i 1[j=i]+(1-d_i)z_j/R. This matrix is
column-stochastic, has the required diagonal bounds, and maps p to o. When R=0,
all occupied true-route columns have d_i=1; their identity columns suffice, and
unoccupied columns can be completed arbitrarily subject to their bounds.

Thus p lies exactly in the simplex capped by u_i=min(1,o_i/d_i), with u_i=1
when d_i=0. Strictly positive p exists exactly when every cap is positive and
their sum is at least one. The sharp bounds for Q=p_A²/(p_W p_M) follow by
fixing p_A: the denominator is maximized by balancing W/M as their caps permit,
and minimized at an endpoint of the feasible W interval. The minimum occurs at
the least feasible A and the maximum at its cap. Zero and infinity are limits,
approached by mixing closure witnesses with any positive feasible point.

This exactness concerns lower diagonal bounds. The construction can increase
diagonal probabilities above d_i; it does not solve a model fixing the diagonal
exactly, a known full confusion matrix, or a classifier shared across arms or
contexts. Those additional constraints can tighten identification. Nor does the
construction establish native transport of known-truth control performance.

Retaining U is consequential: o=(1/5,1/5,1/5,2/5), d_i=3/5 forces a uniform
latent triad and Q=1. Renormalizing the observed triad gives caps 5/9 and the
entire limiting Q range [0,infinity]. Such renormalization can be explicitly
conservative, but it is a different observation contract. If an unrestricted
true-Other class is admitted without a lower bound on the true-triad fraction,
all positive conditional triad compositions become feasible when all three
observed route probabilities are positive. A known lower triad fraction beta>0
instead gives exact caps min(1,o_i/(beta*d_i)); sufficiency takes that fraction
equal to beta and assigns the remaining residual through the Other column.

For counts, simultaneous observed-label upper bounds and known-truth correct-call
lower bounds give conservative caps. With C contexts there are 12C one-sided
limits, so tail allocation alpha/(12C) and a union bound suffice under valid
marginal count laws and the declared transport inequality. Across-cell
independence is unnecessary. Projecting through Q, baseline/selected ratios and
the common-J intersection preserves this simultaneous guarantee. Overlapping
outer intervals do not establish shared-classifier feasibility or equality.

`independent_oracle.py` imports no producer code. Its polygon vertex/edge
optimizer agrees with the proposed formulas for 729 rational cap vectors; it
also checks 46,509 positive latent grid points, 8,100 classifier completions,
and 16,200 true-Other completions. `count_coverage_oracle.py` hash-pins the
preserved CP engine before importing it. It exhaustively checks 1,758,276
baseline/selected count pairs for each of two J=1 population scenarios with
50 endpoint units per arm and 40 known-truth control units per route/arm.
Noncoverage probabilities are approximately 1.3434e-18 and 2.4755e-19,
below the allocated per-context 0.025. Each enumeration includes 3,060
nonvacuous projected J intervals. This is **per-context coverage under a
two-context allocation**, not a four-arm common-null simulation or power study.
The software checks support the algebraic argument; finite grids are not its
proof.

After the independent oracles were fixed, `compare_frozen_producer.py` checked
producer SHA-256
`66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368`.
All 729 cap cases, 8,100 classifier-completion cases, and 48 one-sided count
limits agreed. All five stored fixture results reproduced exactly, including
their input hashes. The comparison found no mathematical or implementation
defect in the reviewed scope. Its own receipt records the frozen source hashes;
it accepts `--producer` and `--output` for portable re-execution.

The independent scripts use paths relative to their own directory. The count
oracle also accepts `--cp-source` and `--output`. Exact receipts preserve tiny
noncoverage probabilities that round to zero when coverage is printed as a
binary floating-point number. `INDEPENDENT_HASHES.json` intentionally omits its
own digest.

Original review documentation: CC BY 4.0. Original independent oracle code: MIT,
under the repository terms. Prepared with AI assistance.
