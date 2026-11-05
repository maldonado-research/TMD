# TMD methods 0.7.0

[Published archive](https://doi.org/10.5281/zenodo.23970140) · [Download ZIP](TMD_methods_0_7_0_2026-11-04.zip) · [SHA-256](TMD_methods_0_7_0_2026-11-04_SHA256SUMS.txt) · [Publication evidence](research/methods_0_7_0/README.md)

This methods/report release connects learned-threshold calibration, full-cohort eligibility, route classification and future count uncertainty under one prespecified total error budget. It also archives the related conditional curvature, design and recovery tools, each with its own contract. The [integrated method](research/integrated_inference/README.md) and [independent review](research/integrated_inference/INDEPENDENT_INTEGRATION_REVIEW.md) explain the coverage argument and its limits.

For `C` fixed contexts, total error `alpha`, and calibration share `w`, the integration assigns `gamma = alpha*w/(2*C)` to each learned gate and `eta = alpha*(1-w)/(14*C)` to each future count endpoint. Under the stated conditional sampling laws and external control-transport premises, the total certificate failure probability is at most `alpha`. Confidence events may be dependent; each future count must still have a valid binomial marginal conditional on all training and calibration data.

In the illustrative allocation `C=2`, `alpha=0.05`, `w=1/8`, each component error is `1/640`. A strict maximum gate with 59 controls gives an upper false-tail bound near 10.37%. The exact minimum for a bound at most 5% under this allocation is 126 controls per gate. This is a conditional arithmetic example, not a native biological sample-size recommendation or a power calculation. A larger calibration maximum can also reduce true-route passage, which requires separate measurement.

All bundled observation tables are synthetic. The release supplies no native control measurements, validated biological mechanism, novel theorem, prospective registration or external peer review. Independent internal computational review checks the implementation and finite examples. Input strings and plan hashes do not establish truth, chronology, independence or transport. The frozen primary forecast comparison and actual study/planning fields are unchanged.

The ZIP contains 169 files and is 498,964 bytes. SHA-256:

```text
575dfdcf1ee55d6c3691038f12dd0e73dcc1edee1e10828d6240789ccc0df4f4
```

After extraction, enter `TMD_methods_0_7_0_2026-11-04/` and run:

```sh
python3 -B run_archive_checks.py --manifest-only
python3 -B run_archive_checks.py --output ../fresh_replay_receipt.json
```

Python 3.10+ and the standard library suffice for those checks. The release replay passed eleven verification jobs, 43 saved fixture checks, three integrated CLI examples, 51 preserved hash entries and comparison of 163 original files with the public source commit. Deterministic rebuilding of the extracted package reproduced the ZIP exactly. The receipt identifies larger historical oracles and excluded source authentication that were not rerun.

The public record retains all eight inherited files unchanged and adds the 0.7.0 ZIP and checksum. All ten file downloads, complete supplied metadata and rendered notes were verified after publication. The [0.6.0 snapshot](https://doi.org/10.5281/zenodo.23219776) remains immutable. This version belongs to report/methods concept [23068055](https://doi.org/10.5281/zenodo.23068055), separate from historical software v2.6.5. No GitHub Release event or automatic-archiving change was made.

Source content: [7bd3f2e](https://github.com/maldonado-research/TMD/tree/7bd3f2e47dd13e4f31a9c60c2c6465f188fe14cb), merged in [PR 49](https://github.com/maldonado-research/TMD/pull/49). Publication date is 4 November 2026 in America/Los_Angeles; source and audit timestamps are 5 November UTC. Original code is MIT and original documentation CC BY 4.0, with preserved attribution. Prepared with AI assistance.
