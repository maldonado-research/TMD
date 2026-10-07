#!/usr/bin/env python3
"""Acquire the pinned public Farr dataset with two requests and a 20MiB cap."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from reproduce_sbw25_audit import DATA_DOI, ZIP_BYTES, ZIP_MD5, ZIP_SHA256

BUDGET = 20 * 1024 * 1024
METADATA_URL = "https://zenodo.org/api/records/14335473"
FILE_KEY = "Zenodo data files 09 dec 2024.zip"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-directory", required=True, type=Path)
    args = p.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    requests, used = [], 0

    def read(url, maximum):
        nonlocal used
        parsed = urlparse(url)
        assert parsed.scheme == "https" and parsed.hostname == "zenodo.org"
        assert parsed.username is None and parsed.password is None
        request = Request(url, headers={"User-Agent": "TMD-original-public-source-audit/1.0"})
        # No credentials, Authorization headers, URL secrets or formula execution.
        with urlopen(request, timeout=45) as response:
            final_url = urlparse(response.geturl())
            assert final_url.scheme == "https" and final_url.hostname == "zenodo.org"
            assert response.status == 200
            data = response.read(min(maximum, BUDGET - used) + 1)
        assert len(data) <= maximum and used + len(data) <= BUDGET
        used += len(data)
        requests.append({"url": url, "status": 200, "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest(),
                         "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        return data

    metadata_bytes = read(METADATA_URL, 1024 * 1024)
    metadata = json.loads(metadata_bytes)
    assert metadata["id"] == 14335473 and metadata["doi"] == DATA_DOI
    assert metadata["metadata"]["license"]["id"] == "cc-by-4.0"
    files = [f for f in metadata["files"] if f["key"] == FILE_KEY]
    assert len(files) == 1
    file = files[0]
    assert file["size"] == ZIP_BYTES and file["checksum"] == "md5:" + ZIP_MD5
    data = read(file["links"]["self"], ZIP_BYTES)
    assert len(data) == ZIP_BYTES
    assert hashlib.md5(data).hexdigest() == ZIP_MD5
    assert hashlib.sha256(data).hexdigest() == ZIP_SHA256
    (args.output_directory / "zenodo_metadata.json").write_bytes(metadata_bytes)
    (args.output_directory / "source_data.zip").write_bytes(data)
    receipt = {"maximum_download_bytes": BUDGET, "maximum_sources": 12,
               "requests": requests, "total_response_bytes": used,
               "authentication_used": False, "zip_md5_verified": ZIP_MD5,
               "zip_sha256_verified": ZIP_SHA256}
    (args.output_directory / "ACQUISITION_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": "passed", "requests": len(requests), "bytes": used,
                      "zip_bytes": len(data), "authentication_used": False}))


if __name__ == "__main__":
    main()
