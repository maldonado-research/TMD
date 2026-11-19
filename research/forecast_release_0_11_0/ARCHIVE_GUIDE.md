# Forecasting which observed lineage leads at the final visit

**Mutation by Natural Dominance · Report and methods supplement 0.11.0 · Ricardo Maldonado**

Does the label with the largest measured share early in a population keep the lead at its last scheduled visit? Does projecting the change between the first two visits improve on using the leader at the second visit? This retrospective study compares those forecast rules against published observations. Each population contributes at most one scored endpoint per rule. The study report gives the eligible populations, visit schedules, score denominators and source limitations. [Study report](https://github.com/maldonado-research/TMD/blob/main/research/lineage_forecasts/README.md) · [Forecast rules](https://github.com/maldonado-research/TMD/blob/main/research/lineage_forecasts/FORECAST.md)

## Check the archive and reproduce the analysis

Run the following command in the directory containing the downloaded ZIP and checksum file.

```sh
sha256sum -c TMD_lineage_forecasts_0_11_0_2026-11-19_SHA256SUMS.txt
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

The offline report is `research/lineage_forecasts/README.md`. Run `bash research/lineage_forecasts/replay.sh` to reproduce the two-lineage results. Follow the reproduction commands in the [study report](https://github.com/maldonado-research/TMD/blob/main/research/lineage_forecasts/README.md). To rebuild the ZIP and checksum from Git, check out the exact `source_commit` in `MANIFEST.json`, create an empty output directory, and run the following command from the repository root.

```sh
python3 -B research/forecast_release_0_11_0/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original code. Creative Commons Attribution 4.0 covers original documentation. Published data retain their original attribution and terms. [Licensing](https://github.com/maldonado-research/TMD/blob/main/LICENSING.md) · [Software license](https://github.com/maldonado-research/TMD/blob/main/LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055) · [Preceding report 0.10.0](https://doi.org/10.5281/zenodo.24379400)
