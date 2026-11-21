# Can founder fitness predict which competitor finishes ahead?

**Mutation by Natural Dominance · Report and methods supplement 0.12.0 · Ricardo Maldonado**

The study tests whether a separate assay of founder fitness helps predict which of two established labels leads at day 25 in published yeast competitions. The report compares two yeast fitness assays on the same outcomes. A separate analysis asks whether growth measured in monoculture predicts the final abundance of competing green-algae species. The archive includes the three count and pool tables carried forward from version 0.11.0. [Study report](https://github.com/maldonado-research/TMD/blob/main/research/founder_fitness/README.md) · [Preceding supplement](https://doi.org/10.5281/zenodo.24382132)

## Check the archive and reproduce the analysis

Run the following command in the directory containing the downloaded ZIP and checksum file.

```sh
sha256sum -c TMD_founder_fitness_0_12_0_2026-11-20_SHA256SUMS.txt
```

Extract the archive into an empty directory. Run this check from the extracted root before running the analysis. It compares every source file with the byte count and SHA-256 digest in the manifest.

```sh
python3 - <<'PY'
from hashlib import sha256
import json
from pathlib import Path

manifest = json.loads(Path('MANIFEST.json').read_text())
entries = manifest['files']
actual = {path.as_posix() for path in Path('.').rglob('*') if path.is_file()}
assert actual == set(entries) | {'MANIFEST.json'}
for name, entry in entries.items():
    data = Path(name).read_bytes()
    assert len(data) == entry['bytes'] and sha256(data).hexdigest() == entry['sha256'], name
print(f"Verified {len(entries)} source files at commit {manifest['source_commit']}")
PY
```

From the extracted root, run `bash research/founder_fitness/replay.sh` to check the saved forecast scores against the included anonymous counts. The offline report at `research/founder_fitness/README.md` gives the separate commands and source data for other comparisons. [Study report](https://github.com/maldonado-research/TMD/blob/main/research/founder_fitness/README.md) · [Green-algae analysis](https://github.com/maldonado-research/TMD/blob/main/research/founder_fitness/algae/README.md)

To rebuild the distribution, check out the repository at the exact `source_commit` in `MANIFEST.json`. Create an empty output directory and run the following command from the repository root.

```sh
python3 -B research/founder_release_0_12_0/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original code. Creative Commons Attribution 4.0 covers original documentation. Source data retain their original attribution and terms. [Licensing](https://github.com/maldonado-research/TMD/blob/main/LICENSING.md) · [Software license](https://github.com/maldonado-research/TMD/blob/main/LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055)
