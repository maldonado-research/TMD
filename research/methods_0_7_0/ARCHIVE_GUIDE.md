# TMD methods 0.7.0: conditional observation and control inference

Methods snapshot dated 4 November 2026 (America/Los_Angeles); source snapshot
and computational audit dated 5 November 2026 UTC. Ricardo Maldonado.
Prepared with AI assistance and independent internal computational review.

This is an executable methods/report snapshot of original TMD software,
mathematical explanations, synthetic examples, and bounded verification. It
adds a connected set of observation and control calculations to the earlier
methods work. It contains no newly admitted native biological data, validated
biological TMD mechanism, new theorem or priority claim, externally peer-reviewed
result, or registered experiment. An archive DOI records the materials; it does
not establish those scientific claims.

The main new integration carries one declared error budget from maximum-selected
threshold calibration through eligibility and wrong-label bounds to simultaneous
curvature intervals. The conditional curvature, design, and recovery modules are
related alternatives with their own contracts. They are not automatically
combined with that integration or with a study's existing score comparisons.
All inferential guarantees remain conditional on the declared sampling,
independent truth, score freezing, denominator, and control-transport premises.
Input declarations and plan hashes record assertions; they do not authenticate
those premises or establish prospective registration.

## Contents

| Directory | Methods scope |
| --- | --- |
| `research/conditional_curvature` | Exact finite conditional tests for known positive offsets or independent matched baselines; includes plug-in counterexamples. |
| `research/conditional_design` | Conditional support geometry, retained information, and complete small-budget synthetic operating probabilities. |
| `research/conditional_recovery` | Two-context differential-recovery sensitivity with externally justified coverage intervals and a fixed reference ordering. |
| `research/classification_bounds` | Wrong-label and unresolved-outcome observation bounds, exact population projection, and conservative count wrappers. |
| `research/eligibility_gate_bounds` | Known-Other controls and full-cohort gate fractions; explicit handling of unidentified eligible fractions. |
| `research/threshold_calibration` | Selection-aware strict/inclusive sample-maximum thresholds, including maximum multiplicity and tie boundaries. |
| `research/integrated_inference` | One declared plan and error allocation connecting threshold, gate, route-control, and count uncertainty. |
| `research/prospective_design/REGISTRY_CANDIDATE.json` | Unchanged historical **unregistered candidate**, included solely because the design verifier checks its integrity. |

The source modules and their existing receipts retain their original bytes.
`SOURCE_PROVENANCE.json` identifies their source commits/hashes and exclusions.
`MANIFEST.json` inventories every archived file except itself. Review receipts
are evidence of executed computational checks, not proof that real observations
satisfy the models. Some broader oracle receipts are preserved by byte identity
rather than fully rerun for packaging.

## Run and verify

Python 3.10 or later is required. The inference engines, fixtures, archive
checks, and listed verification commands use only the standard library.
Regenerating the optional classification illustration also requires NumPy and
Matplotlib; the existing PNG and SVG are included. No network access or source
download is needed for the bounded archive replay.

After extraction, change into `TMD_methods_0_7_0_2026-11-04/` and run:

```sh
python3 -B run_archive_checks.py --manifest-only
python3 -B run_archive_checks.py --output ../fresh_replay_receipt.json
```

The full command verifies the inventory and preserved review hashes, creates an
isolated temporary copy, runs each included producer verifier, reruns selected
independent comparisons, and checks regenerated receipts and synthetic fixtures
against the archived versions. It leaves this extracted archive unchanged.
Each producer-verification process has a 240-second bound; very slow systems
may time out. The command's receipt distinguishes checks freshly executed from
source authentication or larger oracle runs that were not repeated.

The integrated example can be evaluated separately:

```sh
python3 -B research/integrated_inference/integrated_inference.py \
  --plan research/integrated_inference/example_strict_separation_plan.json \
  research/integrated_inference/example_strict_separation_observations.json \
  --repository .
```

For a plan-only calculation, supply `--plan-only` and omit the observation file.
This is a design calculation, not registration or evidence that calibration
has been performed. Standalone verifier scripts often regenerate adjacent
receipts; use the isolated archive runner above or copy the package to scratch.

To rebuild an identical ZIP from an unchanged extracted package using the
same Python/zlib implementation:

```sh
python3 -B build_archive.py --package . --output-directory ../rebuilt
```

The builder sorts entries, fixes ZIP timestamps and permission fields, and
uses fixed compression settings. The SHA-256 checksum file authenticates the
complete ZIP, including its internal manifest. ZIP compression bytes may differ
between zlib implementations; the file-content manifest remains comparable.

## Source boundaries and context references

Original explanatory notes, bibliographic references, source hashes, and public
aggregate summaries are included where useful. No raw third-party article
bodies, noncommercial source copies, source-author software, individual human
sample metadata, private inventories, credentials, caches, or Python bytecode
are bundled. The few excluded classification source-audit files are explicitly
listed in `SOURCE_PROVENANCE.json`; their absence changes no runtime dependency
or numerical method.

Original module links to broader TMD material retain their source wording.
Those context files are outside this narrow archive. Resolve them using the
links in [CONTEXT_REFERENCES.md](CONTEXT_REFERENCES.md), or the repository and
exact source commit in `SOURCE_PROVENANCE.json`, for example
`https://github.com/maldonado-research/TMD/blob/<commit>/<path>`. The archive
does not require those online context references to run its methods.

The eligibility source-audit scripts require separately obtained, hash-matched
source bodies, which are deliberately excluded. Their historical receipts
are not freshly authenticated by the archive runner. The recovery measurement
bridge can replay its synthetic arithmetic without an article and explicitly
reports `PASS_COUNTEREXAMPLE_SOURCE_UNRUN`. Absence of source replay must not be
read as a fresh verification of literature claims.
Source-provenance receipts may identify excluded cached responses or broader
repository files; those are evidence references, not the archive inventory.

## Relationship to earlier releases and licensing

The intended publication family is the existing report/methods concept
[10.5281/zenodo.23068055](https://doi.org/10.5281/zenodo.23068055).
Methods 0.6.0 is the separate, immutable 1 October snapshot published as
[10.5281/zenodo.23219776](https://doi.org/10.5281/zenodo.23219776).
This snapshot does not replace or regenerate any earlier archive. Historical
software v2.6.5, record 22398093, belongs to a different family.

Original code is MIT, with copyright © 2026 Ricardo Maldonado; see `LICENSE`.
Original documentation is CC BY 4.0; see `LICENSING.md`. Preserve attribution
to Ricardo Maldonado, the TMD repository, and this version or source commit.
The pinned confidence kernel retains its original MIT notice and
`research/classification_bounds/sources/VERSION_LINEAGE.md`. Literature cited
in the original notes keeps its own rights; citations and hashes grant no new
rights to source publications or datasets. Historical licensing references to
files outside this narrow archive do not imply those files are included.
