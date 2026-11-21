# Predicting which mutation class appears in the first observation window

**Mutation by Natural Dominance · Report and methods supplement 0.14.0 · Ricardo Maldonado**

This supplement compares forecasts of the first recorded substitution class when several changes can share one observation window. It also evaluates a random recorded substitution in an independent plant endpoint catalog. The report, source notes, derived data and analysis code are under `research/first_window/`. [Study report](https://github.com/maldonado-research/TMD/blob/main/research/first_window/README.md) · [Preceding supplement](https://doi.org/10.5281/zenodo.24427132)

## Check the archive and reproduce the analysis

Run the following command in the directory containing the downloaded ZIP and checksum file.

```sh
sha256sum -c TMD_first_window_0_14_0_2026-11-21_SHA256SUMS.txt
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

The offline report at `research/first_window/README.md` gives the replay commands, required software and source attribution for each comparison.

To rebuild the distribution, check out the repository at the exact `source_commit` in `MANIFEST.json`. Create an empty output directory and run the following command from the repository root.

```sh
python3 -B research/window_release_0_14_0/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original code. Creative Commons Attribution 4.0 covers original documentation. Source data retain their original attribution and terms. [Licensing](https://github.com/maldonado-research/TMD/blob/main/LICENSING.md) · [Software license](https://github.com/maldonado-research/TMD/blob/main/LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055)
