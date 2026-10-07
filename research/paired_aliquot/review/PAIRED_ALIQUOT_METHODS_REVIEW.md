# Paired aliquots: an observation-model check, not a mutation mechanism

Original independent methods note for TMD R000010, 7 October 2026. This develops established marked-count/compound-Poisson mathematics. No new theorem, sampling-law admission, biological fit, confidence result or mathematical-priority claim is made. No new source was acquired.

## Start with the physical unit

Let `R` be the terminal number of true descendants eligible for a defined genotype measurement in one culture. It is not the number of mutation births, independent founding cultures, all-culture CFUs or sampled sequencing reads. Write its probability-generating function as `H(u)=E[u^R]`.

Assume each descendant independently falls into exactly one of three categories: aliquot 1 with probability `p1`, aliquot 2 with probability `p2`, or omitted with probability `1-p1-p2`. These are **disjoint categories**, with `p1,p2>=0` and `P=p1+p2<=1`. Recorded physical volume fractions alone do not authenticate homogeneous independent capture or genotype recovery.

The paired-count PGF is

`G(z1,z2)=H(1-P+p1 z1+p2 z2)`.

If mutation births are Poisson with mean `m`, independent clone sizes have PGF `g`, and the terminal count is their sum, then `H(u)=exp{m[g(u)-1]}`. Thus

`G(z1,z2)=exp{m[g(1-P+p1 z1+p2 z2)-1]}`.

This conditional model does not authenticate a Poisson mutation process in the SBW25 source. Standing mutants, transfer, selection and different growth histories can create other `H` with the same observed marginals.

## Two useful falsifiable checks

Setting `z1=z2=z` shows that the pooled count `S=X1+X2` has the ordinary one-aliquot thinning law at capture fraction `P`:

`G_S(z)=H(1-P+Pz)`.

For `P>0`, conditional on a pooled count `S=s` having positive probability,

`Pr(X1=j | S=s)=choose(s,j)(p1/P)^j(p2/P)^(s-j)`.

The proof conditions on the captured descendants: each has independent aliquot label 1 with probability `p1/P`. Summing over arbitrary possible `R` leaves that conditional split unchanged. It includes `s=0`, for which both counts are zero; when `P=0`, the split ratio is undefined and the pair is degenerate.

Equivalently, `G(z1,z2)=G_S((p1/P)z1+(p2/P)z2)`. Therefore the joint count probability is `Pr(S=a+b) choose(a+b,a)(p1/P)^a(p2/P)^b`. The same identity holds for coefficients relative to the common joint-zero probability. It supplies a check against a separately implemented multivariate convolution rather than requiring mutation-event counts as data.

These identities hold for **arbitrary terminal history `H`**, including mixtures of clone, mutation, survival and growth histories. They do not require a Poisson birth model, an equal-growth clone law or finite moments. The classical infinite-mean LD model has finite counts almost surely and a well-defined PGF, so these checks remain meaningful even though its count moments cannot be used below.

An experimentally authenticated departure can falsify the stated sampling or classification assumptions. Passing supports only that aspect of the observation model. It does not identify a mutation rate, distinguish mutation from imported/standing variation, validate constant recovery, or confirm TMD. A common unmeasured capture loss in both arms can preserve the split ratio while changing the pooled-count law. Even descendant-specific union-capture probabilities can retain the binomial split if each captured descendant has the same arm-label ratio. The split alone therefore cannot calibrate total detection.

## Conditional versus marginal dependence

Conditional on a known fixed eligible-descendant total `R=N`, multinomial sampling gives

`Cov(X1,X2 | R=N)=-N p1 p2`.

When `R` is random with finite first and second moments,

`Cov(X1,X2)=p1 p2[Var(R)-E(R)]`.

For the compound-Poisson history with finite `E[K^2]`, this becomes

`Cov(X1,X2)=m p1 p2 E[K(K-1)]`.

The Poisson event-number fluctuation and clone-size variability can outweigh the within-history negative covariance. Positive sibling-aliquot covariance is consequently compatible with ordinary clone formation. It does not require a new dominance force. For singleton clones (`K=1`), the disjoint compound-Poisson counts are independent Poisson variables. For the asymptotic law `Pr(K=k)=1/[k(k+1)]`, the first and second moments diverge: do not substitute infinity into these covariance differences or report a finite covariance prediction.

Void probabilities avoid that moment problem. Let `A(p)=1-g(1-p)`. Then

`Pr(X1=0,X2=0)=exp[-m A(P)]`,

while each marginal zero probability is `exp[-m A(pj)]`. The log joint-to-product zero ratio is

`m[g(1-P)-g(1-p1)-g(1-p2)+1]`.

For disjoint probabilities and a nonnegative integer clone law, the bracket is nonnegative. For any fixed `k>=2`, its mixed finite difference equals the integral of the nonnegative second derivative of `(1-p)^k` over the two probability increments. Averaging over `K` preserves the inequality without a moment assumption. Strict positivity requires `m>0`, `p1,p2>0` and positive probability of clones with at least two descendants. This is a conditional CP prediction, not a general law for every random history `H`.

## Overlapping recapture and independent cultures are different frames

If both arms independently capture the **same** descendant and can count it twice, the per-descendant PGF is instead

`(1-p1+p1 z1)(1-p2+p2 z2)`.

The CP joint PGF becomes `exp{m[g((1-p1+p1 z1)(1-p2+p2 z2))-1]}`. With finite moments its covariance is `m p1 p2 E[K^2]`, larger than the disjoint expression by `m p1 p2 E[K]`. Conditional on fixed `R=N`, the two independent recapture counts have zero covariance. This model concerns repeated/overlapping detection, not separate destructive aliquots of cells that cannot occur in both arms.

Its joint-zero probability is `exp[-m A(p1+p2-p1 p2)]`. For equal marginal capture probabilities with `p1+p2<=1`, the CP model predicts that overlapping-recapture joint zeros are at least as frequent as disjoint-aliquot joint zeros, which are at least as frequent as the product of the marginal zeros. These inequalities depend on the declared common CP history and sampling frames, and do not supply a biological fitted rate.

Two physically separate cultures with independent histories and fixed independently controlled parameters have the product of their marginal PGFs and zero covariance. Shared stock, block, batch or other latent variability can violate that product assumption. Labelling two plates from one culture as two cultures does not supply independent histories.

## Exact rational counterexamples

Take a synthetic fixed clone size `K=2`, Poisson birth mean `m=1`, and `p1=p2=1/4`. Both marginal means are `1/2`, both marginal variances are `5/8`, and each marginal has `-log Pr(Xj=0)=7/16`.

| Paired sampling/history frame | `-log Pr(X1=0,X2=0)` | `Cov(X1,X2)` |
|---|---:|---:|
| Disjoint aliquots, one CP culture | `3/4` | `1/8` |
| Independent overlapping recapture, one CP culture | `175/256` | `1/4` |
| Two independent CP cultures | `7/8` | `0` |

All entries are exact rational exponents or moments; the zero probabilities themselves are exponentials of those values, not rational probabilities. Equal marginal measurements therefore do not authenticate the joint physical frame.

As a separate fixed-history contrast, `R=2` with disjoint `p1=p2=1/4` has covariance `-1/8`, marginal zero probabilities `9/16` and joint zero probability `1/4`. Mixing the stated CP histories changes the covariance to positive `1/8`. With singleton CP clones `K=1,m=1`, disjoint counts are independent despite conditional multinomial negative covariance.

## Proposed comparison and its limits

Use fresh independent cultures as the experimental history units, preserving genotype, founder/transformant, occasion and block identifiers. Take paired terminal aliquots from the same well-mixed culture before any further growth. Randomize plate labels and declared volume allocations, record volumes against a common initial-culture denominator, and preserve the physical disjointness of sampled material. Sequential aliquots require accounting for removed volume and any intervening growth or sampling changes.

Authenticate known genotype-control recovery, dilution, cell aggregation, colony-size gates, phenotype lag, post-plating mutation, genotype classification and sequencing frames independently. A colony may arise from a cell clump rather than one independently sampled cell. Aggregate/packet capture can invalidate the cell-count binomial split and make sibling counts informative about the observation unit rather than mutation timing. Plate-specific recovery or differential genotype/age detection can change the split ratio. A common age-dependent gate can remain invisible to that split.

Record raw integer, fully classified paired counts and all zeros; do not use fractional `L/M` corrected candidate counts as if they were such measurements. Preserve culture-level clustering and use a separately justified diagnostic plan rather than adding aliquots to the independent-culture denominator. To compare pooled pairs with a single aliquot of total volume, predefine exchangeable culture arms, identical selection/recovery and their block allocation. A pooled pair and a destructive single aliquot cannot both be observed from exactly the same terminal cells.

No sample size, power, error allocation, stopping rule, registered protocol or confirmatory gate is chosen here. Any future diagnostic error budget must be declared separately without renewing or silently spending the existing TMD confirmatory budget. These notes do not alter the frozen forecast, count-law contract, 26 NULL actual-study fields, R6/R7 source receipts, source acquisition limits or publication rules.

## What was actually read

For this round, the current R7 `conditional_fluctuation.py` and its model/sampling/resource notes were reread. Existing primary context is Farr et al., DOI [10.1371/journal.pgen.1011572](https://doi.org/10.1371/journal.pgen.1011572), and Foster (2006), DOI [10.1016/S0076-6879(05)09012-9](https://doi.org/10.1016/S0076-6879(05)09012-9), previously read and hashed in R7. Neither source is represented as validating this paired-aliquot experiment. No fresh web/source acquisition, biological data fit, author contact, GitHub/Zenodo write or credential access was performed for this note. Original prose only; no raw source or private archive content is included.
