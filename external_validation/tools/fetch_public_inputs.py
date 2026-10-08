#!/usr/bin/env python3
"""Obtain the third-party public inputs of the external-validation analyses into raw/.

They are NOT redistributed in this repository. Every input is pinned and verified:
  A  GitHub DrLizarraga/Closed-Loop-Learning-Based-PID-Tuning-for-DC-Motor-Actuators @ 8c74893a15c2... (MIT)
  B  Mendeley Data 10.17632/5xvg43r9r8 v2 and v1: only the raw logs and parameter tables used (CC BY 4.0)
  C  Zenodo 10.5281/zenodo.21201595 (v1.0.0) and record 21389722 (v2.0.0) archives         (MIT)
Checksums are in ../sources.json.

  python3 tools/fetch_public_inputs.py                 download from the public sources
  python3 tools/fetch_public_inputs.py --cache DIR     copy from an existing raw/ directory, verifying every checksum
"""
import argparse, hashlib, json, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
SRC = json.load(open(ROOT / "sources.json"))


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def get(url, api=False):
    # Mendeley file downloads need a User-Agent; the JSON Accept header is sent only to the Mendeley API
    headers = {"User-Agent": "Mozilla/5.0"}
    if api:
        headers["Accept"] = "application/json"
    for attempt in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=300).read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def candidate_a(cache):
    a = SRC["candidate_A"]; dest = RAW / "candidate_A_github"
    if cache:
        shutil.copytree(Path(cache) / "candidate_A_github", dest, dirs_exist_ok=True)
    elif not dest.exists():
        subprocess.run(["git", "clone", "--quiet", a["repository"], str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "--quiet", a["commit"]], check=True)
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert head == a["commit"], head


def mendeley_listing(dataset_id, version):
    api = "https://data.mendeley.com/public-api/datasets"
    try:
        folders = json.loads(get(f"{api}/{dataset_id}/folders/{version}", api=True))
    except Exception:
        folders = []
    by_id = {f["id"]: f for f in folders}

    def path_of(fid):
        parts = []
        while fid in by_id:
            parts.append(by_id[fid]["name"]); fid = by_id[fid].get("parent_id")
        return "/".join(reversed(parts))
    out = {}
    for fid in ["root"] + [f["id"] for f in folders]:
        for f in json.loads(get(f"{api}/{dataset_id}/files?folder_id={fid}&version={version}", api=True)):
            rel = f"{path_of(fid)}/{f['filename']}" if fid != "root" else f["filename"]
            out[rel] = f["content_details"]["download_url"]
    return out


def candidate_b(cache):
    for key, sub in (("candidate_B_v2", "candidate_B_mendeley"), ("candidate_B_v1", "candidate_B_mendeley_v1")):
        spec = SRC[key]
        listing = None
        for rel, h in spec["required_files_sha256"].items():
            dest = RAW / sub / "files" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if cache:
                shutil.copy2(Path(cache) / sub / "files" / rel, dest)
            elif not dest.exists() or sha(dest) != h:
                listing = listing or mendeley_listing(spec["dataset_id"], spec["version"])
                dest.write_bytes(get(listing[rel]))
            if sha(dest) != h:
                sys.exit(f"checksum mismatch {sub}/{rel}")


def candidate_c(cache):
    dest = RAW / "candidate_C_zenodo"; dest.mkdir(parents=True, exist_ok=True)
    for key in ("candidate_C_v1", "candidate_C_v2"):
        spec = SRC[key]; f = dest / spec["file"]
        if cache:
            shutil.copy2(Path(cache) / "candidate_C_zenodo" / spec["file"], f)
        elif not f.exists():
            f.write_bytes(get(spec["download_url"]))
        if sha(f) != spec["sha256"] or hashlib.md5(f.read_bytes()).hexdigest() != spec["md5"]:
            sys.exit(f"checksum mismatch {f.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--cache"); a = ap.parse_args()
    candidate_a(a.cache); candidate_c(a.cache); candidate_b(a.cache)
    print("all public inputs present and verified")
