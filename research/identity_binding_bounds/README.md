# Conditional bounds when a row crosswalk is incomplete

Ricardo Maldonado · 27 October 2026 · Original project analysis with AI assistance using standard finite-set bounds.
All numerical examples below are synthetic. This note supplies no native data,
biological fit, new mathematical theorem, or TMD validation.

R43 showed that two incompatible score-to-barcode bindings can both pass its
structural preflight. A useful next step is to report exactly which descriptive
associations survive **every** binding compatible with independently authenticated
records. This quantifies the information supplied by a partial crosswalk without
inventing the remaining identities.

## Conditional frame

Assume two lists refer to the same fixed frame of `n` distinct individual rows:

- A result list with a fixed binary predicate, such as a supplied finite estimate
  being greater than zero. Let `a` results satisfy it. This is a numerical
  predicate, not a claim of adaptation, significance, or mutation origin.
- An identity list with a fixed binary **source-label grouping**, with `c` in the
  named group. The complement is a source-label complement, not an independently
  verified genotype-negative group.

Assume a bijection connects the lists. Some pairs have authenticated provenance;
every bijection of the remaining rows is initially allowed. The frame, one-to-one
relationship, row roles, source labels and anchors are external assumptions. Equal
lengths or successful R43 preflight do not establish them. Population, experiment
and run restrictions must be respected before defining a free pool.

## Sharp anchor bounds

Let `k` distinct authenticated pairs contain `a_K` predicate-positive results,
`c_K` named-group identities, and `x_K` pairs positive on both sides. Remove those
paired entries and write

\[
m=n-k,\qquad a_F=a-a_K,\qquad c_F=c-c_K.
\]

For the full-frame overlap `x`, the complete feasible set is

\[
x\in\{L,L+1,\ldots,U\},\quad
L=x_K+\max(0,a_F+c_F-m),\quad
U=x_K+\min(a_F,c_F).
\]

Require nonnegative integer counts, `0 <= a_F,c_F <= m`, and nonnegative
anchor-table cells `x_K`, `a_K-x_K`, `c_K-x_K`, and
`k-a_K-c_K+x_K`. Conflicting, reused or duplicate anchor endpoints are invalid.
For `m=0`, the interval is the singleton `x_K`.

**Proof.** In the free pool, an overlap `z` cannot exceed either marginal and the
union has size `a_F+c_F-z <= m`; these give the bounds. Conversely, choose `z`
predicate-positive free rows and `c_F-z` predicate-negative free rows for the
named-group identities. Both selections exist exactly when those inequalities
hold. Assign the remaining identities arbitrarily within the complement. This
constructs a bijection for every integer `z` in the stated range and proves
sharpness for this unrestricted free-pool model. No probability distribution over
bindings is assumed.

When `0 < c < n`, the difference between the numerical-predicate fractions is

\[
D(x)=\frac{x}{c}-\frac{a-x}{n-c}
    =\frac{nx-ac}{c(n-c)}.
\]

Therefore its exact feasible values are `D(L), D(L+1), ..., D(U)`, not every real
number between the endpoints. Strict positive association survives all permitted
bindings precisely when `nL > ac`; strict negative association survives precisely
when `nU < ac`. A singleton association need not identify the full crosswalk.
If `c=0` or `c=n`, this between-group difference is undefined.

## Entirely synthetic example

Take `n=8`, `a=4`, `c=4`. With no anchors, `x=0,...,4` and
`D=-1,-1/2,0,1/2,1`: both signs are possible.

Now suppose three distinct predicate-positive results are independently bound to
three named-group identities. Then `k=a_K=c_K=x_K=3`, leaving
`m=5`, `a_F=c_F=1`. The allowed overlaps are `x=3,4`, giving
`D=1/2,1`. A positive **source-label association** survives the remaining identity
ambiguity, conditional on the stated frame and anchors. It does not establish
genotype truth, causality, biological adaptation or a native TMD claim.

An independent finite enumeration checks the entire attainable overlap set for
714,520 combinations of margins and exact injective partial matchings through
`n=6`. Run `python3 research/identity_binding_bounds/verify_bounds.py` from the
repository root. The enumeration checks finite cases; the constructive proof
supplies the general result. No source-author code or biological simulation was
executed.

## Practical use and falsifiability

1. Obtain immutable, run-linked result/identity records and the role/retention
   manifest. Preserve their checksums, original rows, terms, nominal time labels,
   and unresolved clock conventions. Reconcile individuals, aggregates, padding,
   exclusions, missing identities and annotations before declaring a shared frame.
2. Supply independent crosswalk evidence for each anchor. Preserve its original
   identifiers and source location. Never select a pairing because its scores
   make the association stronger. An anchor obtained by such reasoning is an
   assumption, not independently authenticated identity evidence.
3. Freeze the descriptive predicate, label meaning, compatible blocks and target
   statistic. Count and validate the anchored and free margins. Produce the exact
   bounds and explicit endpoint assignments. Keep all unresolved biological and
   native-admission flags false.
4. A later authenticated complete crosswalk can check the conditional calculation:
   its overlap must lie in the feasible set if all premises remain true. An
   overlap outside it contradicts at least one frame, label, anchor or computation
   premise; it does not identify which premise failed or demonstrate author error.

If external records restrict which free pairs are possible, the formula above
remains an outer bound but need not be sharp. Use only permitted bipartite edges
and minimize/maximize the overlap over perfect matchings. No feasible perfect
matching means the supplied records and assumed frame cannot all be satisfied.
The minimum and maximum in a restricted graph do not imply that every integer
between them is attainable; restrictions can leave gaps in the feasible set.
Independent complete population/run blocks can instead use the formula per block
and sum their overlap endpoints; that is sharp when every within-block free
binding is allowed. Pooled association can still reflect differences between
blocks and has no causal interpretation.

## Limits and relation to prior work

Duplicates, many-to-one barcode clustering, unaccounted aggregates, padding,
missing numerical rows or uncertain frame membership break this bijection model.
They require a different explicitly justified frame/model; dropping them or
inventing extra rows is not a repair. Unknown annotations must remain unknown. A
complete identity frame can support a declared label-present versus label-absent
comparison, but absence is never silently recoded as a negative molecular assay.
If complete group membership cannot be declared, these fixed-`c` formulas cannot
answer the intended genotype comparison. Uncertain anchors likewise require
expanding the allowed bindings rather than treating them as verified.

The bounds describe deterministic identity ambiguity. They are neither confidence
intervals nor a random-permutation test, and they include no sampling uncertainty,
classification error, loss/establishment correction, mutation-birth denominator,
time calibration or native transfer. A robust descriptive sign cannot certify any
of those missing measurements.

A scoped local review of R41–R43 and a Markdown keyword search through
`/workspace/TMD/research` and `MATHEMATICAL_EXTENSION.md` found related established
work: R41 bounds clone CDFs under repeated-row weighting; R43 gives the two-binding
counterexample and structural checker; R20 uses Fréchet union bounds for event
capture; the earlier transport analysis gives interval bounds for recovery
mismatch. This note applies familiar finite-set intersection bounds to partial
identity crosswalks. It does not assert global novelty or replace those analyses.

No R42 grouped counts are substituted into these equations: their biological
individual-row frame, bijection, annotation meaning and execution linkage are
unverified. No study/planning NULL, frozen predictor/comparator, error allocation,
stopping rule, methods 0.6.0 artifact, or paused runner is changed by this note.
