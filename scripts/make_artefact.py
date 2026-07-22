#!/usr/bin/env python3
"""Dispatch input D-B: record a deliberate artefact digest as a stampable JSON.
A sha256 + a short label + the time it was recorded — nothing else, no body.
Filename: artefacts/<UTC-date>-<label>.json
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

sha = (os.environ.get("ART_SHA") or "").strip().lower()
label_raw = (os.environ.get("ART_LABEL") or "").strip()

if not sha:
    print("no artefact_sha256 provided; skipping artefact step")
    sys.exit(0)
if not re.fullmatch(r"[0-9a-f]{64}", sha):
    print(f"artefact_sha256 must be 64 lowercase hex chars; got {sha!r}",
          file=sys.stderr)
    sys.exit(2)

label = re.sub(r"[^a-z0-9-]+", "-", label_raw.lower()).strip("-") or "artefact"
now = datetime.now(timezone.utc)
doc = {
    "sha256": sha,
    "label": label,
    "computed_at": now.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
}
os.makedirs("artefacts", exist_ok=True)
path = f"artefacts/{now.strftime('%Y-%m-%d')}-{label}.json"
with open(path, "w") as f:
    json.dump(doc, f, sort_keys=True, separators=(",", ":"))
    f.write("\n")
print(f"wrote {path}")
