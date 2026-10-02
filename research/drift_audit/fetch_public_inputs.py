#!/usr/bin/env python3
"""Fetch only an explicit small-file allowlist through read-only GitHub API calls.

Uses the existing gh authentication route; never reads or displays credentials.
No external Python dependencies. Raw third-party inputs remain in ignored raw/.
"""
import argparse
import base64
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

REPOSITORY = "joaoascensao/genetic-drift-evolution"
COMMIT = "c1b47a977a9307281917ac1dee29861a813a7fd2"
TREE = "f7df5cc44e2a648a9e9215e55d46620ce4daa7fc"
LIMIT_BYTES = 20_000_000
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
BOOTSTRAP = {
    "repository.json": f"repos/{REPOSITORY}",
    "commit_main.json": f"repos/{REPOSITORY}/commits/main",
    "tags.json": f"repos/{REPOSITORY}/tags?per_page=100",
    "commit_Genetics.json": f"repos/{REPOSITORY}/commits/{COMMIT}",
    "tree_via_commit_Genetics.json": f"repos/{REPOSITORY}/git/trees/{COMMIT}?recursive=1",
    "tree_Genetics.json": f"repos/{REPOSITORY}/git/trees/{TREE}?recursive=1",
}
PATHS = ["README.md", "experiments.csv"] + [
    f"{directory}/{prefix}_{suffix}.csv"
    for directory, prefix in [("E1", "E1"), ("E23", "E3"), ("E4", "E4"), ("E5", "E5"), ("E6", "E6")]
    for suffix in ["meta", "exps", "cfus"]
] + ["code/HMM_stan.py", "code/HMM_stan_combinereps.py"]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Refetch metadata and selected inputs; default reuses raw cache.")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    previous_manifest_path = ROOT / "INPUT_MANIFEST.json"
    previous_manifest = json.loads(previous_manifest_path.read_text()) if previous_manifest_path.exists() else {}
    for evidence in previous_manifest.get("reused_previous_round_evidence", []):
        path = ROOT / evidence["file"]
        if not path.exists():
            raise RuntimeError("Previously recorded local protocol/license evidence is missing; restore the SHA-pinned snapshot before refetching")
        data = path.read_bytes()
        if len(data) != evidence["bytes"] or sha256(data) != evidence["sha256"]:
            raise RuntimeError("Previously recorded protocol/license evidence changed; review instead of silently rewriting provenance")
    api_records = []
    downloaded = 0
    wire_bytes = 0

    def get(filename, endpoint):
        nonlocal downloaded, wire_bytes
        local = RAW / filename
        if local.exists() and not args.refresh:
            response = local.read_bytes()
        else:
            remaining = LIMIT_BYTES - wire_bytes
            if remaining <= 0:
                raise RuntimeError("Download budget exhausted")
            proc = subprocess.Popen(["gh", "api", endpoint, "--method", "GET"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            chunks = []
            while True:
                chunk = proc.stdout.read(min(65536, remaining + 1))
                if not chunk:
                    break
                remaining -= len(chunk)
                if remaining < 0:
                    proc.kill()
                    proc.wait()
                    raise RuntimeError("Stopped at cumulative 20 MB budget")
                chunks.append(chunk)
            proc.stderr.read()
            if proc.wait() != 0:
                raise RuntimeError(f"Read-only GitHub API request failed: {endpoint}")
            response = b"".join(chunks)
            downloaded += len(response)
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(response)
        wire_bytes += len(response)
        if wire_bytes > LIMIT_BYTES:
            raise RuntimeError("Cached and new API responses exceed cumulative 20 MB audit budget")
        api_records.append({"file": f"raw/{filename}", "endpoint": f"https://api.github.com/{endpoint}", "bytes": len(response), "sha256": sha256(response), "redistribute_by_default": False})
        return json.loads(response)

    meta = {name: get(name, endpoint) for name, endpoint in BOOTSTRAP.items()}
    if meta["repository.json"]["private"]:
        raise RuntimeError("Source is not public")
    if meta["commit_Genetics.json"]["sha"] != COMMIT:
        raise RuntimeError("Pinned commit mismatch")
    tags = {tag["name"]: tag["commit"]["sha"] for tag in meta["tags.json"]}
    if tags.get("Genetics") != COMMIT:
        raise RuntimeError("Release tag has changed; review rather than automatically importing")
    tree = meta["tree_Genetics.json"]
    if tree.get("truncated"):
        raise RuntimeError("Incomplete source tree")
    if tree["sha"] != meta["commit_Genetics.json"]["commit"]["tree"]["sha"]:
        raise RuntimeError("Commit-to-tree mismatch")
    entries = {entry["path"]: entry for entry in tree["tree"] if entry["type"] == "blob"}
    inputs = []
    for source_path in PATHS:
        entry = entries[source_path]
        if entry["size"] > 100_000:
            raise RuntimeError("Allowlisted file exceeds small-file threshold")
        response_file = f"ghapi_blobs/{entry['sha']}.json"
        blob = get(response_file, f"repos/{REPOSITORY}/git/blobs/{entry['sha']}")
        if blob["encoding"] != "base64":
            raise RuntimeError("Unexpected API blob encoding")
        data = base64.b64decode(blob["content"])
        git_hash = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if git_hash != entry["sha"] or len(data) != entry["size"]:
            raise RuntimeError("Pinned blob content verification failed")
        destination = RAW / "inputs" / source_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        inputs.append({"path": source_path, "local_file": str(destination.relative_to(ROOT)), "source_url": f"https://github.com/{REPOSITORY}/blob/{COMMIT}/{source_path}", "git_blob_sha1": git_hash, "sha256": sha256(data), "bytes": len(data), "redistribute_by_default": False})
    manifest = {
        "audit_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repository": f"https://github.com/{REPOSITORY}",
        "repository_public": True,
        "source_release": "Genetics",
        "source_commit": COMMIT,
        "source_tree": tree["sha"],
        "source_commit_date": meta["commit_Genetics.json"]["commit"]["committer"]["date"],
        "main_at_inspection": meta["commit_main.json"]["sha"],
        "complete_tree_entries": len(tree["tree"]),
        "api_response_bytes_cumulative_in_audit": wire_bytes,
        "download_bytes_in_this_invocation": downloaded,
        "max_cumulative_api_response_bytes": LIMIT_BYTES,
        "raw_reads_and_archive_downloaded": False,
        "github_license_field": meta["repository.json"].get("license"),
        "license_paths_found_in_complete_tree": [path for path in entries if "license" in path.lower() or "copying" in path.lower()],
        "api_responses": api_records,
        "inputs": inputs,
    }
    inherited = []
    for name, source_url, description in [
        ("drift_zenodo_21431096.json", "https://zenodo.org/api/records/21431098", "Previously retrieved metadata response resolves to version record 21431098; archive not downloaded."),
        ("drift_preprint_pmc.xml", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12873942/", "Previously retrieved January 2026 preprint XML, not the journal Methods."),
    ]:
        path = RAW / "evidence" / name
        if path.exists():
            data = path.read_bytes()
            inherited.append({"file": str(path.relative_to(ROOT)), "source_url": source_url, "description": description, "bytes": len(data), "sha256": sha256(data), "new_download_in_this_round": False, "redistribute_by_default": False})
    manifest["reused_previous_round_evidence"] = inherited
    zenodo_path = RAW / "evidence" / "drift_zenodo_21431096.json"
    if zenodo_path.exists():
        record = json.loads(zenodo_path.read_text())
        if record.get("id") != 21431098 or record["metadata"].get("version") != "Genetics":
            raise RuntimeError("Unexpected archived release metadata")
        manifest["archive_license_provenance"] = {
            "doi": record["doi"], "record_id": record["id"],
            "license_id": record["metadata"]["license"]["id"],
            "release_link_in_record": record["metadata"]["related_identifiers"],
            "archive_bytes": record["files"][0]["size"],
            "archive_downloaded_or_checksum_verified": False,
            "limit": "Archive metadata license is verified; GitHub has no license declaration in inspected tree. Archive bytes were not compared with GitHub blobs. Raw inputs remain excluded from public outputs.",
        }
    (ROOT / "INPUT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"source_commit": COMMIT, "selected_files": len(inputs), "cumulative_response_bytes": wire_bytes, "new_bytes": downloaded}))


if __name__ == "__main__":
    main()
