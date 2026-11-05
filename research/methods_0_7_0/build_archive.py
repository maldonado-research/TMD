#!/usr/bin/env python3
"""Deterministically package a reviewed TMD methods tree without network calls.

Copyright (c) 2026 Ricardo Maldonado. MIT; see package/LICENSE.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    default_package = here / "package" if (here / "package").is_dir() else here
    parser.add_argument("--package", type=Path, default=default_package)
    parser.add_argument("--output-directory", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    package = args.package.resolve()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in package.rglob("*") if p.is_file() and p.name != "MANIFEST.json")
    for path in files:
        assert not path.is_symlink(), path
        assert path.suffix not in (".pyc", ".pyo"), path
        assert not any(part.startswith(".") or part == "__pycache__" for part in path.relative_to(package).parts), path
    assert not args.output_directory.resolve().is_relative_to(package), "Write release artifacts outside the package tree"
    manifest = {"schema_version": 1, "version": "0.7.0", "release_date": "2026-11-04", "release_date_timezone": "America/Los_Angeles", "snapshot_date_utc": "2026-11-05", "algorithm": "sha256", "self_exclusion": "MANIFEST.json is the only unlisted archive file; ZIP hash authenticates it.", "files": [{"path": str(p.relative_to(package)), "bytes": p.stat().st_size, "sha256": digest(p)} for p in files]}
    (package / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    stem = "TMD_methods_0_7_0_2026-11-04"
    output = args.output_directory / (stem + ".zip")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in package.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(stem + "/" + str(path.relative_to(package)), date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    checksum = digest(output)
    (args.output_directory / (stem + "_SHA256SUMS.txt")).write_text(checksum + "  " + output.name + "\n")
    print(json.dumps({"filename": output.name, "bytes": output.stat().st_size, "sha256": checksum, "archive_files": len(files) + 1}, indent=2))


if __name__ == "__main__":
    main()
