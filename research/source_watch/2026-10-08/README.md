# Does the new mutation-bias theory supply a TMD comparator?

Original critical assessment · R24 · 8 October 2026, America/Los_Angeles

Park and Krug's [*Mutation-biased adaptation: The Yampolsky–Stoltzfus model revisited*](https://doi.org/10.64898/2026.10.05.756661), version posted **7 October 2026**, gives a timely conventional explanation to assess before interpreting a TMD residual. The authors develop approximate fixation probabilities between rare-origin and abundant-mutation regimes. This is an unreviewed preprint; its reported agreement with simulations is not independently replayed here.

The primary HTML URL returned the abstract and metadata. A subsequent official PDF retrieval through Firecrawl returned a parsed representation with all **14 pages** reported processed. The review covers the abstract, Model and Discussion, selected strong/weak-selection derivations, and Appendix C. The parser duplicates some mathematical fragments and converts graphical material into apparent tables. Those fragments and apparent tables are not numerical inputs; the raw PDF bytes were not downloaded or hashed. Raw source representations stay outside Git. This is source and model-scope assessment, not a verified implementation of the authors' equations.

## First establishment and ultimate fixation differ

The model starts with a single ancestral genotype in a constant-size haploid, asexual Wright–Fisher population. Two beneficial mutations can arise from that ancestor; subsequent mutation from the mutant states is forbidden. Its target is **ultimate fixation**, rather than the first established lineage or the first recovered colony. Strong- and weak-selection treatments have distinct assumptions.

In the strong-selection approximation, a less-fit mutant can establish first and still lose when a fitter competitor establishes while it grows. The authors retain continuing mutation input and a competitor's establishment chance that changes with population composition. A supply-times-single-introduction-establishment comparator can therefore omit an ordinary source of endpoint dependence. Its failure would not by itself establish a distinct natural-dominance mechanism.

TMD already warns about clonal interference in its [formulation](../../FORMULATION_AND_NEXT_EMPIRICAL_TEST.md). The new source makes the next measurement question concrete: **do independently observed competing lineages establish during the interval between the first establishment and the declared endpoint?** Record allele-resolved trajectories, founding ancestry, divisions/bottlenecks, observation windows and missing lineages. A large nominal culture, endpoint mutation fraction or fitted effective population size cannot answer that question.

## A least-fit marginal is not a three-route forecast

The Outlook and Appendix C extend the strong-selection approximation to the **least-fit genotype** among more than two alternatives. They do not provide every component of a general three-route fixation vector. Pairwise approximations or renormalization of one marginal do not supply the missing vector. The weak-selection extension also leaves the general multi-route solution open.

Consequently, this paper cannot directly furnish the full Wsp/Aws/Mws forecast, the independently measured supply baseline, target-context eta, common theta, mutation-origin inclusion or an admitted biological count law. Its illustrative comparison with an earlier bacterial endpoint experiment uses inferred historical parameters and is not a frozen held-out TMD test. No parameter is transferred.

| Decision for a future study | Evidence needed before inference |
| --- | --- |
| Are rare-origin approximations appropriate? | Independently justified origin, demographic and establishment measurements, with losses and subsequent competing establishments retained. Absence of detected competition alone is insufficient without detection controls. |
| Does interference matter for the chosen endpoint? | Time-resolved coexisting lineages and an admitted observation model connecting establishment to that endpoint. Serial transfer, changing environments and compound genotypes require their own model. |
| Is a conventional comparator complete? | A complete probability vector for the same observed categories, from independently admitted inputs, frozen before held-out outcomes. A single marginal cannot fill it. |
| Can the TMD restriction be assessed? | The existing matched biological, recovery, count-law and frozen-forecast contract; all 26 actual study inputs remain unresolved. |

These are refinements to the scientific assessment packet, not selected study settings. The [prospective design](../../prospective_design/README.md) and its forecasts, axis, eta rule, uncertainty allocation and stopping remain unchanged. Qualified biological/statistical assessment is still required before choosing a real protocol. No new theorem, new biological observation, validated comparator, power result or breakthrough is claimed.

## Recent search and reused evidence

Two targeted paper-index searches with requested dates 2025–8 October 2026 returned twelve records. They are a bounded search, not an entire-web or systematic review; an index's date filtering does not independently authenticate publication dates. The 2025 preprint and 2026 journal entries for Barber and Couce are one evidence family. Their [2026 primary article](https://doi.org/10.1038/s41467-026-74044-6) was already assessed in [R4](../2026-10-02/README.md). Reacquisition adds no independent cohort or biological outcome. The other search candidates remain metadata/abstract leads rather than new admitted evidence.

The same round authenticates new official PTATO catalog/sample metadata in [the processed-metadata audit](../../processed_metadata/README.md). That concrete artifact advance has priority over implementing another mathematical extension. All 18 native-control planning fields remain unresolved. The published methods 0.6.0 archive freezes the earlier 1 October snapshot and excludes this R24 addendum.

## Verify the captured source representations

Arrange the three response snapshots named in [SOURCES.json](SOURCES.json) in an external cache. Run the standard-library checker from the repository without changing the package:

```sh
python research/source_watch/2026-10-08/verify_sources.py \
  --source-cache /path/to/r24-source-cache > /tmp/tmd-r24-source-check.json
```

The saved [receipt](VERIFICATION_RECEIPT.json) passes 37 response/parsed-representation identity and selected-anchor checks. These checks do not validate the authors' approximations or authenticate biological measurements. A changed or unavailable source snapshot must be resolved explicitly rather than substituted silently.

Original commentary CC BY 4.0; new verification code MIT. Source authors retain their rights. Prepared by Ricardo Maldonado with AI assistance; independent internal review is separate from external peer review.
