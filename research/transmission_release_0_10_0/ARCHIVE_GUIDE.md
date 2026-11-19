# Inherited outcomes and evidence of mutation timing

**Mutation by Natural Dominance · Report and methods supplement 0.10.0 · Ricardo Maldonado**

Which observations establish that an outcome was inherited, and which can establish when it first arose? This report traces the evidence to published plant records and yeast observations. The analyses retain the units of the original studies, including offspring in a maternal family, marker calls in one specimen, and populations or lineages at recorded sampling times. Each comparison identifies the assumptions that connect those observations to the first successful heritable route. [Research report, sources and individual analyses](https://github.com/maldonado-research/TMD/blob/main/research/transmission_timing/README.md)

Version 0.10.0 corrects an earlier source-coverage statement. Ji et al. report site-specific measurements for the original focal peach leaf. Two of 59 reads supported M101 and 15 of 32 supported M71. The two-read and three-read cutoffs yield different relationships between the marker sets across the 75 leaves. A separate workbook records explicit marker calls for seven progeny of the tree. [Correction and source counts](https://github.com/maldonado-research/TMD/blob/main/research/transmission_timing/peach/S7_CORRECTION.md) · [Progeny crosswalk](https://github.com/maldonado-research/TMD/blob/main/research/transmission_timing/peach/S11_CROSSWALK.md) · [Original leaf workbook](https://doi.org/10.1371/journal.pgen.1011829.s021) · [Original progeny workbook](https://doi.org/10.1371/journal.pgen.1011829.s025)

In the pine study, any rule assigning one phenotype to each linked-marker genotype disagrees with at least 129 of the 571 offspring points displayed in Figure 7. In the yeast time series, omitting a later visit changes both the earliest qualifying marker group and its first qualifying generation in one population. The pine and yeast analyses use different observation units and retain separate results. [Pine figure audit](https://github.com/maldonado-research/TMD/blob/main/research/transmission_timing/pine/FIGURE7.md) · [Yeast timing comparison](https://github.com/maldonado-research/TMD/blob/main/research/transmission_timing/yeast/TIMING_CHECK.md)

## Verify the archive and run the calculations

In the extracted archive, open `research/transmission_timing/README.md` for the report with links to local figures and source notes.

From the directory containing the ZIP and the SHA-256 checksum sidecar, run the first command. Extract the ZIP into an empty directory. The commands that follow run from the extracted root with Python 3.10 or later.

```sh
sha256sum -c TMD_transmission_timing_0_10_0_2026-11-19_SHA256SUMS.txt
```

```sh
python3 - <<'PY'
from hashlib import sha256
import json
from pathlib import Path
manifest = json.loads(Path('MANIFEST.json').read_text())
entries = manifest['files']
assert {p.as_posix() for p in Path('.').rglob('*') if p.is_file()} == set(entries) | {'MANIFEST.json'}
for path, entry in entries.items():
    data = Path(path).read_bytes()
    assert len(data) == entry['bytes'] and sha256(data).hexdigest() == entry['sha256'], path
print(f"Verified {len(entries)} source files at {manifest['source_commit']}")
PY
bash research/transmission_timing/replay.sh
```

The study folder contains the remaining reproduction commands. The manifest gives each member’s Git source path, byte count and SHA-256 digest. To rebuild from Git, check out the precise `source_commit` in the manifest and run the builder at that revision, supplying an existing output directory.

```sh
python3 -B research/transmission_release_0_10_0/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original code. Creative Commons Attribution 4.0 covers original documentation. Source studies retain their attribution and terms. The terms are included in `LICENSING.md` and `LICENSE` in the archive. [Project licensing](https://github.com/maldonado-research/TMD/blob/main/LICENSING.md) · [Software license](https://github.com/maldonado-research/TMD/blob/main/LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055) · [Preceding archive 0.9.1](https://doi.org/10.5281/zenodo.24378187)
