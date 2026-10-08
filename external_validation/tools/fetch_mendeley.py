#!/usr/bin/env python3
"""Download every file of a public Mendeley Data dataset version and verify SHA-256.

Usage: python3 fetch_mendeley.py <dataset_id> <version> <out_dir>
Writes <out_dir>/_mendeley_metadata.json, _mendeley_files.json and the files
in their folder structure. Fails if any downloaded file's hash differs from
the hash Mendeley reports.
"""
import hashlib, json, sys, time, urllib.request
from pathlib import Path

API = "https://data.mendeley.com/public-api/datasets"


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            return data if binary else json.loads(data)
        except Exception as e:  # retry transient errors
            if attempt == 3:
                raise
            time.sleep(2 + 3 * attempt)


def main():
    ds, ver, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    meta = get(f"{API}/{ds}?version={ver}")
    (out / "_mendeley_metadata.json").write_text(json.dumps(meta, indent=2))
    try:
        folders = get(f"{API}/{ds}/folders/{ver}")
    except Exception:
        folders = []
    (out / "_mendeley_folders.json").write_text(json.dumps(folders, indent=2))
    by_id = {f["id"]: f for f in folders}

    def path_of(fid):
        parts = []
        while fid and fid in by_id:
            parts.append(by_id[fid]["name"])
            fid = by_id[fid].get("parent_id")
        return "/".join(reversed(parts))

    listing = []
    for fid in ["root"] + [f["id"] for f in folders]:
        files = get(f"{API}/{ds}/files?folder_id={fid}&version={ver}")
        rel_dir = "" if fid == "root" else path_of(fid)
        for f in files:
            f["_rel_path"] = f"{rel_dir}/{f['filename']}" if rel_dir else f["filename"]
            listing.append(f)
    (out / "_mendeley_files.json").write_text(json.dumps(listing, indent=2))
    bad = []
    for f in listing:
        cd = f["content_details"]
        dest = out / "files" / f["_rel_path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest() != cd["sha256_hash"]:
            dest.write_bytes(get(cd["download_url"], binary=True))
        h = hashlib.sha256(dest.read_bytes()).hexdigest()
        if h != cd["sha256_hash"]:
            bad.append(f["_rel_path"])
    print(f"{len(listing)} files, {len(folders)} folders, {len(bad)} hash mismatches {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
