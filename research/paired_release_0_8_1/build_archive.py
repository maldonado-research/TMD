"""Rebuild the 0.8.1 report supplement and its SHA-256 sidecar from one Git commit."""
import argparse
import hashlib
import io
import json
import os
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

REPO = Path(__file__).resolve().parents[2]
RELEASE = "research/paired_release_0_8_1"
GUIDE = f"{RELEASE}/ARCHIVE_GUIDE.md"
BUILDER = f"{RELEASE}/build_archive.py"
PAIRED = "research/paired_evidence"
ROBUSTNESS = "research/archived_rank_robustness"
EARLIER = "research/archived_route_ranks"
EARLIER_FILES = ["README.md", "OBSERVATION_CHECK.md", "audit.py", "rank_result.json"]
REQUIRED = {GUIDE, BUILDER, "LICENSE", "LICENSING.md", "research/FORMULATION_AND_NEXT_EMPIRICAL_TEST.md", *(f"{EARLIER}/{f}" for f in EARLIER_FILES),
            f"{PAIRED}/README.md", f"{PAIRED}/verify_paired.py", f"{PAIRED}/verify_peach.py",
            f"{ROBUSTNESS}/howells_receipt.json", f"{ROBUSTNESS}/rank_margins.py"}
STEM = "TMD_paired_evidence_0_8_1_2026-11-18"


def git(*args):
    return subprocess.check_output(["git", "--no-replace-objects", "-C", REPO, *args])


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def package(commit):
    entries = git("ls-tree", "-r", "-z", commit, "--", PAIRED, ROBUSTNESS, EARLIER, *sorted(REQUIRED))
    files, sources = {}, {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        mode, kind, object_id = metadata.split()
        if mode not in (b"100644", b"100755") or kind != b"blob":
            raise ValueError(f"Expected a regular file at {path}")
        if Path(path).suffix.lower() in {".xls", ".xlsx", ".xlsm"}:
            raise ValueError(f"Download third-party workbooks from their credited source: {path}")
        if "__pycache__" in Path(path).parts or Path(path).suffix in {".pyc", ".pyo"}:
            continue
        data = git("cat-file", "blob", object_id.decode("ascii"))
        name = "README.md" if path == GUIDE else path
        files[name] = data
        sources[name] = {"source_path": path, "bytes": len(data), "sha256": sha256(data)}
    missing = REQUIRED - {entry["source_path"] for entry in sources.values()}
    if missing:
        raise ValueError(f"Missing release sources: {', '.join(sorted(missing))}")
    if files[BUILDER] != Path(__file__).read_bytes():
        raise ValueError("Run the builder from the chosen source commit.")
    manifest = {
        "version": "0.8.1",
        "source_repository": "https://github.com/maldonado-research/TMD",
        "source_commit": commit,
        "concept_doi": "10.5281/zenodo.23068055",
        "previous_version_doi": "10.5281/zenodo.24356344",
        "files": sources,
    }
    files["MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    stream = io.BytesIO()
    with ZipFile(stream, "w") as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return stream.getvalue()


def write_assets(directory, assets):
    for name, data in assets.items():
        previous = directory / name
        if previous.exists() and previous.read_bytes() != data:
            raise FileExistsError(f"Different file already exists: {previous}")
    with tempfile.TemporaryDirectory(dir=directory) as staging:
        for name, data in assets.items():
            staged = Path(staging) / name
            staged.write_bytes(data)
            try:
                os.link(staged, directory / name)
            except FileExistsError:
                if (directory / name).read_bytes() != data:
                    raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True, help="Source commit or ref in this checkout")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd(), help="Existing output directory")
    args = parser.parse_args()
    try:
        commit = git("rev-parse", "--verify", "--end-of-options", f"{args.commit}^{{commit}}").decode().strip()
        archive = package(commit)
        name = f"{STEM}.zip"
        checksum = f"{sha256(archive)}  {name}\n"
        write_assets(args.output_dir, {name: archive, f"{STEM}_SHA256SUMS.txt": checksum.encode("ascii")})
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
    print(checksum, end="")
