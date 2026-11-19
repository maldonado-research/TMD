# Leaf mutation carriers and physical branch topology

**Mutation by Natural Dominance · Report and methods supplement 0.9.0 · Ricardo Maldonado**

Which features of a plant’s growth history can be recovered from leaves that carry the same mutation? Wang et al. recorded 48 mutation sites across 75 bulk leaf samples from one peach tree. Ten pairs of sites have crossing sets of listed leaves. A model that treats each leaf as a single terminal cell lineage, assumes complete observation and allows each mutation once with permanent inheritance cannot represent those pairs. Multiple cell populations in one leaf and incomplete detection can each affect the recorded sets. The archive examines these limits and compares genetic distances with independently measured branch geometry in four tropical trees. [Report and detailed source notes](research/leaf_lineages/README.md)

## Source studies

- **Peach leaf samples.** The DHQ1 tree sample roster and locus records come from Wang et al.’s original S1 and S2 Data. The supplied TSVs transcribe the publisher’s rendered spreadsheets, including specimen identifiers. The physical-position analysis also uses the published branch labels and figure. [Wang et al.](https://doi.org/10.1371/journal.pbio.3000191) · [S1 Data](https://doi.org/10.1371/journal.pbio.3000191.s018) · [S2 Data](https://doi.org/10.1371/journal.pbio.3000191.s019)
- **Peach flower aliquots.** Ji et al.’s tables describe a later set of technical measurements from the same tree. The source notes identify the measured units and their relation to the earlier marker inventory. [Ji et al.](https://doi.org/10.1371/journal.pgen.1011829) · [Previous methods supplement](https://doi.org/10.5281/zenodo.24377555)
- **Tropical tree architecture.** Satake et al.’s Supplementary file 1b reports physical and genetic distances between sampled points in four trees. The analysis compares the branch partitions favored by those measured distances. [Satake et al.](https://doi.org/10.7554/eLife.88456) · [Distance source and calculations](research/leaf_lineages/tropical/TROPICAL.md)

These retrospective data address lineage interpretation under stated measurement assumptions. Biological validation of the first successful mutation-route prediction remains open. The separate prospective split-read prediction uses its previously published eligibility and scoring rules. [Frozen prediction](https://github.com/maldonado-research/TMD/blob/e752c59c78f8b0f6995c6fffc4f3dfbcd0e4bc4e/research/shared_misses/PREDICTION.md)

## Verify the archive and run the calculations

From the directory containing the ZIP and the SHA-256 checksum sidecar, run the first command. Extract the ZIP into an empty directory. The commands that follow run from the extracted root with Python 3.10 or later.

```sh
sha256sum -c TMD_leaf_lineages_0_9_0_2026-11-19_SHA256SUMS.txt
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
python3 -B research/leaf_lineages/carrier/carrier_sets.py | diff - research/leaf_lineages/carrier/carrier_result.json
```

The study folder contains the remaining reproduction commands. The manifest gives each member’s Git source path, byte count and SHA-256 digest. To rebuild from Git, check out the precise `source_commit` in the manifest and run the builder at that revision, supplying an existing output directory.

```sh
python3 -B research/leaf_release_0_9_0/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original code. Creative Commons Attribution 4.0 covers original documentation. Source studies retain their attribution and terms. [Project licensing](LICENSING.md) · [Software license](LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055) · [Preceding archive 0.8.2](https://doi.org/10.5281/zenodo.24377555)
