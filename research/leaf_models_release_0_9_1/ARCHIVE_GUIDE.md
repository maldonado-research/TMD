# Mutation records in peach leaves and grapevines

**Mutation by Natural Dominance · Report and methods supplement 0.9.1 · Ricardo Maldonado**

One peach leaf in the DHQ1 catalogue illustrates how an inference depends on the measurement model. With a cost of one per added site–leaf membership and a cost of three per removed listing, both states of M101 in leaf DHQ1_B1-1-L1 occur among the best compatible tables. If removal costs more than three, all optimal tables list M101 there. If removal has a positive cost below three, all optimal tables leave that entry unlisted. These thresholds follow from an exact calculation on 48 reported markers and 75 leaves. Determining the state in the physical leaf requires an independent measurement. The report is in `research/leaf_models/README.md` in the ZIP. [Report on GitHub](https://github.com/maldonado-research/TMD/tree/main/research/leaf_models)

Another calculation holds every bulk-leaf call fixed while allowing each leaf to contain multiple cell lineages. Under a single irreversible origin per marker, at least 20 leaves require more than one lineage signature. Five require at least three. A single tree realizes these lower bounds across all 75 leaves. These are model-dependent minimum counts of signatures in a mathematical reconstruction. The studies do not measure the number of cells carrying a mutation or the first successful heritable route specified by TMD. [Wang et al.](https://doi.org/10.1371/journal.pbio.3000191) · [Original diagram](https://doi.org/10.1371/journal.pbio.3000191.g004)

The archive includes the normalized peach carrier and sample tables and the transcription of the published figure used in the previous report. The archived scripts replay the calculations from these local inputs. Each file has a source path and checksum. [Sample roster](https://doi.org/10.1371/journal.pbio.3000191.s018) · [Mutation carrier table](https://doi.org/10.1371/journal.pbio.3000191.s019) · [Preceding study](https://doi.org/10.5281/zenodo.24377898)

The grapevine comparison uses a separate 185-vine study. After excluding three markers whose specimen and genotype-class entries disagree, the two source presentations agree on 53 markers. Twelve of 1,378 marker pairs that were indistinguishable in the first 50 vines gained a third observed binary pattern with 135 more vines. None of the 1,378 pairs displayed all four patterns. [Study and native workbook](https://doi.org/10.1093/hr/uhaf237) · [Source comparisons and limitations](research/leaf_models/grape/GRAPES.md)

## Verify the archive and run the calculations

From the directory containing the ZIP and the SHA-256 checksum sidecar, run the first command. Extract the ZIP into an empty directory. The commands that follow run from the extracted root with Python 3.10 or later.

```sh
sha256sum -c TMD_leaf_models_0_9_1_2026-11-19_SHA256SUMS.txt
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
bash research/leaf_models/replay.sh
```

The study folder contains the remaining reproduction commands. The manifest gives each member’s Git source path, byte count and SHA-256 digest. To rebuild from Git, check out the precise `source_commit` in the manifest and run the builder at that revision, supplying an existing output directory.

```sh
python3 -B research/leaf_models_release_0_9_1/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original code. Creative Commons Attribution 4.0 covers original documentation. Source studies retain their attribution and terms. The terms are included in `LICENSING.md` and `LICENSE` in the archive. [Project licensing](https://github.com/maldonado-research/TMD/blob/main/LICENSING.md) · [Software license](https://github.com/maldonado-research/TMD/blob/main/LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055) · [Preceding archive 0.9.0](https://doi.org/10.5281/zenodo.24377898)
