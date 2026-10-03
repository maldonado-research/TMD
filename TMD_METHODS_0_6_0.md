# Reviewed TMD methods 0.6.0 publication candidate

Ricardo Maldonado · 2 October 2026 · Unpublished on Zenodo

[Download the reviewed package](TMD_methods_0_6_0_2026-10-02.zip) · [Verify SHA-256](TMD_methods_0_6_0_2026-10-02_SHA256SUMS.txt) · [Current publication state](research/PUBLICATION_STATUS.md)

This package combines the earlier recovery-transport sensitivity calculation with methods 0.5.0's conservative finite-sample confidence intervals. It retains all 160 published synthetic studies and applies exact rational interval correction, 800 sensitivity decisions and 40 compatibility-frontier certificates. All 44 extracted tests, independent oracle checks and packaging/privacy review pass. The original strict floating-fixture portability audit remains failed and documented; these checks do not conceal it.

All 40 strong-departure synthetic examples reject at hypothetical differential recovery factor 1.25, and none at 1.5. A constructed recovery-only counterexample demonstrates why unaccounted recovery mismatch can imitate biological curvature. These are methods and simulations: no new biological measurements, general power, causal mechanism, new mathematical priority or external peer review is claimed.

## In more basic terms

A route may appear common because mutations arise more often, mutant lineages establish more often, or the assay recovers them more often. The method reports how conclusions change under independently justified uncertainty about recovery. It does not decide which biological explanation is true from winner counts alone.

The 54-file archive preserves 48 original candidate files byte-for-byte and changes packaging/status material only. It freezes methods source commit `465850ee33f746cf42f1b3d5075fba2ea57332ad`; later drift, eligibility and prospective-design rounds are separate GitHub work. [Package review receipt](research/METHODS_0_6_0_PACKAGE_REVIEW.json) gives executed checks and exact hashes. The [independent mathematical review](research/METHODS_0_6_0_MATH_REVIEW.md) is public. Paths in the packaging receipt identify historical external validation locations; reproduction commands and scientific source are included in the archive.

The final archive is 1,277,802 bytes, SHA-256 `72173d93fad40ce6d5b3a9e5db9b18e5804a0509c18866f56cfc3c66baa1de76`, MD5 `963beb4de39cb94a95443425f7fdac49`. The intended concept DOI is 10.5281/zenodo.23068055. Former draft [23113326](https://zenodo.org/records/23113326) is now published with the six inherited 0.5.0 files and no version label. This 0.6.0 ZIP is absent from that record. The labelled 0.5.0 release remains record 23075312; consult [current publication status](research/PUBLICATION_STATUS.md) before staging a coordinated new version.

New code is MIT and new documentation CC BY 4.0; inherited source attribution and terms remain. AI assistance and independent internal review are disclosed.
