# R25: genotype-stage denominator audit

The archived PTATO figure workflow can select a variant for one sample because it passed eligibility in another. It also averages category frequencies without explicitly adding zero-count sample/category rows. These rules have precise, checkable consequences. **Their effect on the actual study results remains unknown:** no variant or callable-locus input was replayed in this audit.

This is an original examination of source code acquired in R23, developed into a reproducible input contract and two small constructed checks. It adds no biological observation or mathematical priority claim. The companion R25 source-inventory assessment supplies a separate, bounded advance in artifact and scalar-summary authentication.

## What the reference frame means

Figure2.R selects all four PTA samples, including the FANCC sample marked `Training=Yes`. Its reference variants come from the code-selected preceding clone, must have SMuRF `CLONAL` and nonfailed-QC states there, and must have preceding-clone VAF strictly above 0.2. The comparison excludes chromosome 17. This is a conditioned caller-derived genotype frame. It is not a complete independently known positive/negative truth catalogue or an origin catalogue.

The predecessor and WT label maps, training flags, chromosome exclusion, global variant membership and ancestry limitations were already identified in R23/R24. They remain requirements for replay, not additional independent evidence. The [replay contract](GENOTYPE_REPLAY_CONTRACT.json) gives the exact sample map, input dependencies, ordered label rules and exclusions.

## A global variant set differs from eligibility within each sample

For one reference SNV row per sample and variant key, let `R_s` be sample s's reference set and `E_s` its subset with final PTATO label PASS or FAIL. The script builds `G`, the union of `E_s` over all samples, then selects `L_s = R_s intersect G` within each sample. Therefore:

```text
E_s is contained in L_s.
X_s = L_s minus E_s
    = (R_s minus E_s) intersect (union of E_t over other samples t).
|L_s| = |E_s| + |X_s|.
```

The two rules agree exactly when `X_s` is empty. Repeated keys within one sample need the row-index version in the [audit](DENOMINATOR_AUDIT.json); uniqueness must be checked before using this set version.

The following is a **constructed example**, not study data:

| Sample | Variant | PTATO final label | SCAN2 final label |
| --- | --- | --- | --- |
| A | v | PASS | PASS |
| B | v | LOW_COV | PASS |
| B | w | FAIL | ABSENT |

Here `E_A={v}`, `E_B={w}` and `G={v,w}`. B's sample-specific denominator is one; the literal global-membership denominator is two. The PTATO description changes from 100% FAIL to 50% FAIL and 50% LOW_COV. SCAN2 PASS changes from 0/1 to 1/2 on these chosen reference rows. This proves the rules are not universally equivalent; it does not establish that any actual row is affected.

The label combination is possible because PTATO applies QC and coverage overrides after caller labels, whereas SCAN2 applies PASS membership last. The source SCAN2 set also includes loaded RESCUE records. A sample-specific `E_s` subset neutralizes this particular shared QC/coverage contrast because its PTATO PASS/FAIL rows have passed those masks. The global subset need not do so. **`E_s` is itself selected using PTATO outcomes:** changing to it does not create an independent or neutral caller-validation truth set.

## A missing category row differs from a zero frequency

Fix a caller and reference frame. Let `m` be the number of sample groups with a positive denominator and `k_c` the number with a positive count for category c. The code's available-row mean and a complete equal-sample mean obey the ordinary averaging identity

```text
sparse category mean = (m / k_c) × zero-completed equal-sample mean,
```

when `k_c>0`. A category absent everywhere has no sparse mean row; its complete mean is zero. Categories must form a retained partition, and omitted or zero-denominator samples require a separate ledger.

For a second **constructed example**, sample A has one PASS and no FAIL; B has no PASS and three FAIL:

| Summary | PASS | FAIL | Sum |
| --- | --- | --- | --- |
| Mean of present category rows | 1 | 1 | 2 |
| Equal-sample mean including zeros | 1/2 | 1/2 | 1 |
| Pooled fraction of four rows | 1/4 | 3/4 | 1 |

A displayed total row count therefore cannot identify which average was calculated. Actual `k_c` values must be reported before interpreting the source summary. These descriptive calculations supply no independent-cell or independent-origin count law.

## Further literal-replay checks

The ordered contract preserves the following source behavior:

* PTA VAF below 0.2 is flagged before a high PTAprob can overwrite the label with FAIL. Predecessor eligibility instead requires VAF strictly above 0.2. Boundary and missing values must be audited.
* `FAIL_VAF` is absent from the plotted factor levels and can become factor NA after the earlier NA-to-ABSENT conversion. Preserve pre-display counts.
* BED starts enter `IRanges` without a `+1` adjustment. The actual file convention and affected endpoints are unverified. Literal reproduction and any conventional-coordinate comparison must be separately named.
* Caller-derived uniqueness uses earlier VCF columns and omits failed-QC states in a row sum. Neither an earlier zero call state nor an omitted missing state authenticates a new mutation origin.

The [audit JSON](DENOMINATOR_AUDIT.json) provides exact line/hash anchors, category-specific denominator definitions and a separately declared sample-specific eligibility analysis. A faithful replay must retain the original semantics before comparing an alternative. No source-result error is claimed here.

## Reproduction and scientific boundary

The pinned inputs are `Figures/Figure2.R` and `Figures/GeneralFunctions.R` from [ProjectsVanBox/PTATO v1.0.1, Zenodo 8186323](https://doi.org/10.5281/zenodo.8186323). Their SHA256 values are recorded in the contract and receipt. Source code and datasets remain external.

Run:

```sh
python3 -B verify_denominator_audit.py --figure-dir /path/to/external/archived/Figures
sha256sum -c SHA256SUMS.txt
```

The verifier authenticates both cached code files, checks 19 line anchors and evaluates the two declared examples with exact rational arithmetic. It makes no network requests, does not execute R and does not replay the paper's numerical results. Missing or changed external source bytes prevent source verification. The [receipt](AUDIT_VERIFICATION_RECEIPT.json) records the checks actually run.

Inherited or standing variants, dropout, reference/copy state, repair differences, selection, drift, lineage loss and technical ascertainment remain ordinary competing explanations. Genotype recovery cannot establish independent ancestry/episode truth or native event inclusion. No mutation-production rate, TMD biological fit or cancer-prevention result follows.

All 26 actual study inputs and 18 native-control planning values remain NULL. Forecasts and eta requirements, count laws, error allocations, stopping rules and the provider-workflow pause remain unchanged. The immutable 1 October Zenodo 0.6.0 archive excludes later R1–R25 work. This internal review does not replace qualified external scientific review.

Original documentation and analytical JSON are CC BY 4.0; the new verifier is MIT under repository terms. Prepared with AI assistance. Publication is restricted to [PUBLIC_FILES.json](PUBLIC_FILES.json); no external source body, variant table, callable-locus record or private archive is included.
