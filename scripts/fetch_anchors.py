#!/usr/bin/env python3
"""Read anchors from the spine's execute-only RPC and materialise anchor JSON
files + latest.json. HEADS AND PROOFS ONLY — never bodies.

Catch-up safe: writes every anchor between the local max seq and the spine's
latest, so a run after an outage commits all missing anchors in order.

Fails RED (nonzero exit) — the H4 alert floor — if:
  * the newest anchor is stale: computed_at older than 26h, or
  * any fetched anchor carries discrepancy = true, or
  * there is a gap in the seq series on the spine.

Reads only public fields via public.get_public_anchor(); the anon key is an
execute-only surface (no table read, no write).
"""
import glob
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

SPINE_URL = os.environ["SPINE_URL"].rstrip("/")
ANON_KEY = os.environ["SPINE_ANON_KEY"]
STALE_HOURS = 26
ANCHOR_DIR = "anchors"

PUBLIC_FIELDS = ["seq", "computed_at", "new_count", "total_count",
                 "batch_hash", "prev_head", "head", "algo", "discrepancy"]
LATEST_FIELDS = ["seq", "computed_at", "new_count", "total_count",
                 "prev_head", "head", "algo", "discrepancy"]


def rpc(p_seq):
    body = json.dumps({} if p_seq is None else {"p_seq": p_seq}).encode()
    headers = {"apikey": ANON_KEY,
               "Content-Type": "application/json",
               "Accept": "application/json"}
    # Legacy anon keys are JWTs and want a Bearer header; modern publishable
    # keys (sb_publishable_...) are authenticated via the apikey header only.
    if ANON_KEY.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {ANON_KEY}"
    req = urllib.request.Request(
        f"{SPINE_URL}/rest/v1/rpc/get_public_anchor",
        data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            rows = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"RPC HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}",
              file=sys.stderr)
        raise
    if not isinstance(rows, list):
        raise SystemExit(f"unexpected RPC response (not a list): {rows!r}")
    return rows[0] if rows else None


def parse_ts(s):
    # PostgREST renders timestamptz as e.g. 2026-07-22T02:45:00.123456+00:00
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def local_max_seq():
    m = 0
    for p in glob.glob(f"{ANCHOR_DIR}/*.json"):
        name = os.path.basename(p)[:-5]
        if name.isdigit():
            m = max(m, int(name))
    return m


def write_json(path, doc):
    with open(path, "w") as f:
        json.dump(doc, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")


def main():
    latest = rpc(None)
    if latest is None:
        print("spine has no anchors yet; nothing to do")
        return 0
    L = int(latest["seq"])

    # --- freshness gate (H4) ---
    age_h = (datetime.now(timezone.utc)
             - parse_ts(latest["computed_at"])).total_seconds() / 3600.0
    if age_h > STALE_HOURS:
        print(f"STALE: newest anchor seq {L} computed_at {latest['computed_at']} "
              f"is {age_h:.1f}h old (> {STALE_HOURS}h floor)", file=sys.stderr)
        return 3

    lo = local_max_seq()

    # --- gather new anchors (catch-up), verify contiguity ---
    fetched = {}
    for s in range(lo + 1, L + 1):
        row = rpc(s)
        if row is None:
            print(f"GAP: seq {s} missing from spine (latest={L})", file=sys.stderr)
            return 5
        fetched[s] = row

    # --- discrepancy gate on everything we are about to publish + the head ---
    for row in list(fetched.values()) + [latest]:
        if row.get("discrepancy") is True:
            print(f"DISCREPANCY: anchor seq {row['seq']} has discrepancy=true",
                  file=sys.stderr)
            return 4

    # --- write (only after gates pass) ---
    os.makedirs(ANCHOR_DIR, exist_ok=True)
    for s, row in sorted(fetched.items()):
        write_json(f"{ANCHOR_DIR}/{s:06d}.json",
                   {k: row[k] for k in PUBLIC_FIELDS})
        print(f"wrote {ANCHOR_DIR}/{s:06d}.json")
    write_json("latest.json", {k: latest[k] for k in LATEST_FIELDS})
    print(f"latest.json -> seq {L} ({'+' + str(len(fetched)) if fetched else 'no'} new)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
