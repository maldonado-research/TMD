# Split plant tissues and the observation of somatic variants

**Mutation by Natural Dominance · Report and methods supplement 0.8.2 · Ricardo Maldonado**

In one peach flower, Ji et al. reported variant-supporting reads in both technical subsamples of some tissues and in just one subsample of others. Among 64 tissue–site comparisons with two or more alternate reads, 14 placed every alternate read in one half. Uniform allocation at the observed depths and alternate totals gives an expectation of 3.18. The source study helped define the analysis and the direction of a future prediction. The underlying number of biological mutations that both halves missed remains unknown. [Ji et al.](https://doi.org/10.1371/journal.pgen.1011829)

## What the archive contains

- **Shared negatives and read allocation.** The first report reconstructs read depths, compares the observed split pattern with a conditional sampling model, and bounds missed positives under explicit assumptions. A separate tropical-tree audit reconciles the numbers of selected and targeted sites in two trees. The folder contains original calculation scripts and derived aggregate tables. [Analysis](research/shared_misses/README.md) · [Reproduction commands](research/shared_misses/REPRODUCE.md) · [Tropical-tree study](https://doi.org/10.1073/pnas.2313312121)
- **Site selection and the interpretation of split comparisons.** The second report follows the measured units back to the source studies and examines which conclusions depend on how observations entered the comparison. Its README identifies source inputs, analytical assumptions and reproduction commands. [Analysis and calculations](research/split_selection/README.md)
- **Prospective test.** The dated specification from 19 November 2026 sets the eligibility rules, dataset ordering, missing-data handling, exact scoring and failure condition. The independent outcome remains pending at preparation of this supplement. [Prediction and instructions](research/shared_misses/PREDICTION.md) · [Frozen GitHub specification](https://github.com/maldonado-research/TMD/blob/e752c59c78f8b0f6995c6fffc4f3dfbcd0e4bc4e/research/shared_misses/PREDICTION.md)

The general TMD hypothesis concerns the first successful heritable route under specified conditions. A measurement made after splitting one plant tissue cannot distinguish when an evolutionary route arose, whether it established, and how often investigators recovered it. Links to earlier reports outside the two packaged research folders can be followed in the source repository at the commit recorded in the manifest. [TMD formulation](https://github.com/maldonado-research/TMD/blob/fabb303d63073af1f4e756a23817d7a64616f432/research/FORMULATION_AND_NEXT_EMPIRICAL_TEST.md)

## Verify and reproduce

From the directory holding the ZIP and its checksum sidecar, run the following command. Extract the ZIP into an empty directory. Its root contains this guide, the manifest and the licenses. Each manifest entry records the archive path, original Git path, byte count and SHA-256 digest. The archive root guide corresponds to the release directory's `ARCHIVE_GUIDE.md` in Git.

```sh
sha256sum -c TMD_plant_observation_0_8_2_2026-11-19_SHA256SUMS.txt
```

From the extracted root, these standard-library commands check the recorded contents and run the split-read allocation and prediction checks. The analysis-specific guides describe the remaining aggregate replays and any original-source or plotting dependencies. Use Python 3.10 or later.

```sh
python3 - <<'PY'
import hashlib
import json
from pathlib import Path
manifest = json.loads(Path('MANIFEST.json').read_text())
files = manifest['files']
assert {p.as_posix() for p in Path('.').rglob('*') if p.is_file()} == set(files) | {'MANIFEST.json'}
for path, info in files.items():
    data = Path(path).read_bytes()
    assert len(data) == info['bytes'] and hashlib.sha256(data).hexdigest() == info['sha256'], path
print(f"Verified {len(files)} files from commit {manifest['source_commit']}")
PY
python3 -B research/shared_misses/allocation/verify_read_allocation.py
python3 -B research/shared_misses/allocation/verify_replication.py
```

Rebuilding from the upstream checkout requires Git and Python. Use the exact `source_commit` from the extracted `MANIFEST.json`, check out that revision in a clean clone, then run the bundled builder there. The example assumes the source commit is available locally and the output directory exists. Sorting entries, using stored ZIP members and fixing file timestamps and permissions makes the archive independent of the clock and local compression library.

```sh
python3 -B research/plant_release_0_8_2/build_archive.py --commit HEAD --output-dir /path/to/output
```

The MIT license covers original software and Creative Commons Attribution 4.0 covers original documentation. Credit the primary authors for their measurements. Source workbooks and archive members cited for replay are available from their original deposits. [Licensing and attribution](LICENSING.md) · [Software license](LICENSE) · [Report series](https://doi.org/10.5281/zenodo.23068055) · [Previous version 0.8.1](https://doi.org/10.5281/zenodo.24356808)
