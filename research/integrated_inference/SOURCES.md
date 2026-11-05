# Dependency and mathematical provenance

This integration applies existing maximum-order-statistic tolerance guarantees,
one-sided binomial confidence inversion, union bounds, conditional expectation,
mixture algebra and capped-simplex projection. It makes no claim to a new
theorem or priority for these methods.

The strict maximum guarantee and inclusive maximum proof are documented in
[threshold calibration](../threshold_calibration/README.md), with source
qualification in its [source record](../threshold_calibration/SOURCES.md).
That record identifies directly inspected Tong, Feng and Li (2018),
“Neyman-Pearson classification algorithms and NP receiver operating
characteristics,” *Science Advances* 4(2):eaao1659,
[doi:10.1126/sciadv.aao1659](https://doi.org/10.1126/sciadv.aao1659),
Proposition 1 and Equation (1). This integration inherits that recorded reading
provenance; it does not claim a fresh source review. Wilks (1941) is classical
bibliographic context as qualified there. The gate-mixture and capped-simplex
arguments come from the original TMD eligibility and classification modules.

The distinction between marginal calibration coverage and conditional future
count coverage is explicit in this extension. Averaging the latter and using
one prespecified family error allocation gives the joint guarantee. No
independence between the confidence events is asserted or required.

The following original TMD source bytes were inspected in the repository at
commit `aedfb16`, after the threshold calibration extension. Paths are relative
to the checkout passed with `--repository`; all four are checked before import.
No copies of these modules or new confidence kernels are bundled here.

| Dependency | SHA-256 | Reused functionality |
| --- | --- | --- |
| `research/threshold_calibration/threshold_calibration.py` | `4256ca07cdd4d6e597c4ed2eda28926917e428391aa05710b2f5b962eb616c0b` | Maximum-summary validation and strict/inclusive certificate. |
| `research/eligibility_gate_bounds/eligibility_gate_bounds.py` | `5c5645e83b3f38ecfb8e196bb5332a555ef752ffab42d4315b6ce7ebbf5d2f6f` | Gate lower bound and eligibility-adjusted classification caps. |
| `research/classification_bounds/classification_bounds.py` | `66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368` | Strict bounded parser, certified scalar wrapper, Q/J bounds and common intersection. |
| `research/classification_bounds/sources/boundary_confidence.py` | `23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d` | Preserved original TMD certified CP endpoint engine. |

The verifier independently evaluates exact binomial tails for returned scalar
endpoints; it does not duplicate a CP interval implementation. Its synthetic
fixture and plan hashes record provenance and content integrity. They do not
authenticate truth labels, prospectivity, sampling, transport or data collection.

The SLST source-boundary discussion is inherited from the
[threshold source qualification](../threshold_calibration/SOURCE_BOUNDARY_NOTE.md)
and earlier eligibility source audit. No individual source data or author code
is introduced here, and no numerical native calibration claim is admitted.

Original code is MIT, copyright (c) 2026 Ricardo Maldonado, under
[LICENSE](LICENSE). Original documentation is CC BY 4.0 under repository terms.
Third-party rights remain unchanged. All newly bundled numerical observations
are synthetic.
