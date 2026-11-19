"""Package TMD reports and methods 0.8.0 from one Git commit."""

import argparse
import hashlib
import io
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


REPOSITORY = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://github.com/maldonado-research/TMD"
DIRECTORIES = ("research/archived_route_ranks", "research/finite_roster_audit")
RELEASE = "research/roster_release_0_8_0"
GUIDE = f"{RELEASE}/ARCHIVE_GUIDE.md"
BUILDER = f"{RELEASE}/build_archive.py"
CACHES = {"__pycache__", ".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def git(*args):
    return subprocess.check_output(["git", "--no-replace-objects", "-C", REPOSITORY, *args])


def source_paths(commit):
    entries = git("ls-tree", "-r", "-z", commit, "--", *DIRECTORIES, "LICENSE", "LICENSING.md", GUIDE)
    paths = []
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        path = PurePosixPath(name.decode("utf-8"))
        if CACHES.intersection(path.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        mode, kind, _ = metadata.split()
        if mode not in {b"100644", b"100755"} or kind != b"blob":
            raise ValueError(f"Expected a regular source file at {path}")
        paths.append(str(path))

    required = {"LICENSE", "LICENSING.md", GUIDE}
    required.update(f"{directory}/audit.py" for directory in DIRECTORIES)
    required.update(f"{DIRECTORIES[0]}/{name}" for name in ("historical_receipt.json", "replay_history.py"))
    missing = required.difference(paths)
    if missing:
        raise ValueError(f"Source commit is missing {', '.join(sorted(missing))}")
    return paths


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def archive(commit):
    files = {}
    records = {}
    for path in source_paths(commit):
        name = "README.md" if path == GUIDE else path
        data = git("show", f"{commit}:{path}")
        files[name] = data
        records[name] = {"source_path": path, "sha256": sha256(data), "bytes": len(data)}

    manifest = {
        "title": "Retrospective route rankings and observation audits",
        "version": "0.8.0",
        "source_repository": SOURCE_URL,
        "source_commit": commit,
        "builder": {"source_path": BUILDER, "sha256": sha256(git("show", f"{commit}:{BUILDER}"))},
        "files": records,
    }
    files["MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as package:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True, help="Source commit or ref in this checkout")
    parser.add_argument("--output", type=Path, required=True, help="Destination ZIP path")
    args = parser.parse_args()
    try:
        commit = git("rev-parse", "--verify", "--end-of-options", f"{args.commit}^{{commit}}").decode().strip()
        builder = git("show", f"{commit}:{BUILDER}")
        if Path(__file__).read_bytes() != builder:
            raise ValueError("Run the builder version stored at the selected commit")
        data = archive(commit)
        with tempfile.TemporaryDirectory(dir=args.output.parent) as temporary:
            staged = Path(temporary) / "archive.zip"
            staged.write_bytes(data)
            try:
                os.link(staged, args.output)
            except FileExistsError:
                if args.output.read_bytes() != data:
                    raise ValueError(f"Different file already exists at {args.output}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
    print(f"{sha256(data)}  {args.output}")


if __name__ == "__main__":
    main()
