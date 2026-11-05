# Dependency provenance and reuse

This utility reuses original TMD code from the unchanged classification-bounds
extension. It does not fetch, vendor or execute source-author code from an
external biological study. Python 3.10 or later and the standard library suffice.

The reference checkout was inspected at Git commit
`515c7d3ea236a073dd9c58a4fb03d184697d7ecb`. Paths below are relative to the TMD
repository passed through `--repository`:

| Dependency | SHA-256 | Reuse |
| --- | --- | --- |
| `research/classification_bounds/classification_bounds.py` | `66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368` | Strict bounded parsing, exact caps/Q/J projection, one-sided CP wrapper. |
| `research/classification_bounds/sources/boundary_confidence.py` | `23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d` | Preserved original TMD 0.5.0 certified scalar Clopper–Pearson endpoints. |

Both hashes are checked before inference. The CP hash is checked by the unchanged
classification loader, and its declared hash is additionally checked here.
Imports suppress bytecode writes to the dependency tree. No dependency bytes are
copied into this extension. Changes to either source require explicit review and
an updated pin; the tool refuses an unexpected version.

The earlier classifier README supplies the true-Other/known-beta corollary and
capped-simplex derivation. Its `sources/VERSION_LINEAGE.md` records the CP lineage:
an original standard-library TMD 0.5.0 confidence-projection kernel using known
Clopper–Pearson inversion and Bonferroni projection, not a modification of an
external solver. The gate-mixture inequality here is elementary probability;
there is no mathematical-priority claim.

Original code is MIT, copyright (c) 2026 Ricardo Maldonado, under the accompanying
[LICENSE](LICENSE) and the existing repository/source licenses. Original prose is
CC BY 4.0 under repository terms. All newly supplied numerical artifacts are
synthetic. No personal/private data, external source bodies, native control panel
or external validation result is added.
