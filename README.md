# Mutation by Natural Dominance (TMD)

[Readable project overview](https://maldonado-research.github.io/projects/tmd/) · [All research projects](https://maldonado-research.github.io/)

[Published research report 0.1.0](https://zenodo.org/records/23068056) — source corrections, secondary analysis and prospective timing diagnostic (30 September 2026).


Research software, source audits, and falsifiable tests for Ricardo Maldonado's Mutation by Natural Dominance hypothesis. The aim is to explain and predict which evolutionary routes occur under specified conditions, while separating mutation supply, accessibility, establishment, and observation.

**Status: exploratory research.** This repository provides reproducible calculations and sharper tests. It does not establish TMD as a validated biological theory, a theory of everything, or a new physical law.

## Start here

- [Scientific progress and recent research](SCIENTIFIC_PROGRESS.md): what changed on September 30, 2026, and why.
- [In More Basic Terms](IN_MORE_BASIC_TERMS.md): a plain-language explanation.
- [Mathematical extension](MATHEMATICAL_EXTENSION.md): exact competing-risk derivations, observational equivalence, and a mutation-supply-adjusted WS restriction.
- [Prospective test plan](PROSPECTIVE_TEST_PLAN.md): measurements and outcomes needed for a fair future test.
- [Evidence and claims](EVIDENCE_AND_CLAIMS.md): what is supported, assumed, corrected, or still unknown.
- [Literature review](LITERATURE_REVIEW.md): primary sources, publication status, and data-access limitations.
- [Data audit](DATA_AND_PROVENANCE_AUDIT.md): source reconciliation and corrections to legacy panels.
- [Published rpoB secondary analysis](RPOB_ANALYSIS.md) and [cell provenance](RPOB_SOURCE_PROVENANCE.md): attributed observations from Leehan and Nicholson (2021).

## Reproduce the calculations

The new code uses only the Python standard library. It was verified with the Python versions listed in `VALIDATION.json`. From a checkout of this repository:

```sh
python3 -m unittest -v test_tmd_time_diagnostic.py
python3 analyze_rpob.py
python3 simulate_time_diagnostic.py --outdir regenerated_results
```

The default simulation runs 200 datasets per scenario, 240 independent replicates per dataset, and 399 permutations per test. It is a simulation of the statistical procedure, not a biological experiment. The checked-in outputs are `synthetic_calibration.json`, `synthetic_switching_example.csv`, and `rpob_results.json`. The rpoB script writes `rpob_results.json` beside itself; use a separate checkout if preserving an untouched release.

To analyze the synthetic example:

```sh
python3 tmd_time_diagnostic.py \
  --csv synthetic_switching_example.csv --routes A,B --cuts 1,2 \
  --time-unit arbitrary_simulation_units \
  --cuts-plan fixed_synthetic_design \
  --event-definition first_successful_arrival \
  --independent-replicates --independent-censoring \
  --permutations 1999 --output example_analysis.json
```

The required CSV fields are `replicate_id,context,time,event,route,provenance`. An event is 1 for an exact first successful arrival and 0 for right censoring; censored records have an empty route. Every replicate ID must be globally unique. Provenance is `synthetic`, `observed`, or `literature_transcription`; it is a declaration, not authentication. The current method requires independent units across all records, no delayed entry, independent censoring of time and route conditional on context, and bins chosen before inspecting outcomes. Paired units, shared unmodeled clusters, detection times, and interval-censored observations require a different analysis.

The rpoB endpoint count table cannot be passed into the time diagnostic: it has no first-arrival observations. A failure to reject constant route fractions does not identify a biological mechanism or prove the hypothesis.

## Main results in this release

1. **Source correction:** the Lind et al. (2019) Wsp/Aws/Mws totals 46/41/18 came from separate pathway-isolated strains. They are not competing-route winner frequencies. Duplicate aliases and synthetic timing also cannot become independent biological evidence.
2. **New secondary analysis:** the original rpoB table's three experimental blocks were restored. Medium-specific predictions outperform a pooled prediction in each held-out block, with an exploratory total gain of 13.126 bits for 111 isolates. This reproduces context information in a published dataset; it does not identify TMD's proposed mechanism.
3. **Timing diagnostic:** a stratified, censoring-aware test checks whether route fractions change across prespecified time bins. In the selected null simulations it rejected 12/200 and 9/200 datasets at 5%; an intentionally strong switching alternative was detected in 200/200. Pooling different contexts produced 194/200 rejections under a within-context null, illustrating a confounding failure.
4. **Identifiability result:** a Lomax waiting-time distribution with time-independent route shares can be generated by common frailty, independent route-specific gamma rates, or deterministic decreasing hazards. First-event observations alone cannot distinguish those constructions.

## Versions, citation, and funding

This September 30 research extension is **0.1.0**. Its version is separate from the archived **TMD software v2.6.5**, available in `TMD_v2_6_5_software_release_2026-09-05.zip` and the [published Zenodo record](https://zenodo.org/records/22398093). The historical archive is preserved byte-for-byte. Its fixtures and legacy scientific interpretations must be read alongside the corrections in this repository. The older DOI is not a DOI for this new extension.

Use `CITATION.cff` to cite this repository and separately cite the original papers when using their data. Research and new analysis were prepared with AI assistance and human-directed scope; reproducible code and explicit limitations are provided for review.

This work was independently developed. **Neither EDISON grant 675419 nor MOSBRI grant 101004806 funded TMD.** This repository makes no claim to those grants. Any conflicting legacy repository metadata requires correction; it is not evidence of research funding.

## Reuse

New software: MIT, see [LICENSE](LICENSE). New documentation: CC BY 4.0, see [LICENSING.md](LICENSING.md). Published numerical observations retain attribution and are not presented as newly collected project data. Source publications, figures, and datasets keep their own rights and licenses. `SHA256SUMS.txt` inventories the release files; hashes establish byte integrity, not scientific truth.
