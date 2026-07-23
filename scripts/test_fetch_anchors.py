#!/usr/bin/env python3
"""Unit tests for scripts/fetch_anchors.py main() decision logic.

Exercises every exit path of the freshness / catch-up / discrepancy / gap
gates plus the no-op path, with the spine RPC stubbed (no network). Each test
runs main() in an isolated temp CWD so anchors/ and latest.json are sandboxed.

Run standalone:   python3 scripts/test_fetch_anchors.py
Or with pytest:   pytest scripts/test_fetch_anchors.py
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

# fetch_anchors reads SPINE_URL / SPINE_ANON_KEY at import time; give it dummies.
os.environ.setdefault("SPINE_URL", "https://example.supabase.co")
os.environ.setdefault("SPINE_ANON_KEY", "test-anon-key")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_anchors  # noqa: E402


def _ts(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()


def _anchor(seq, computed_at, discrepancy=False):
    return {
        "seq": seq,
        "computed_at": computed_at,
        "new_count": 10,
        "total_count": 10 * seq,
        "batch_hash": f"batch{seq:02d}",
        "prev_head": f"head{seq - 1:02d}",
        "head": f"head{seq:02d}",
        "algo": "v1",
        "discrepancy": discrepancy,
    }


def _install_spine(anchors_by_seq):
    """Stub fetch_anchors.rpc to serve a fixed {seq: row} map.

    rpc(None) returns the highest-seq row (the spine's latest); rpc(s) returns
    that seq's row, or None when absent (simulating a gap).
    """
    latest_seq = max(anchors_by_seq) if anchors_by_seq else None

    def fake_rpc(p_seq):
        if p_seq is None:
            return anchors_by_seq.get(latest_seq)
        return anchors_by_seq.get(p_seq)

    fetch_anchors.rpc = fake_rpc


def _run_in(tmp_path, existing_anchor_seqs=(), latest_json=None):
    """Set up a sandbox CWD with pre-existing anchor files, then run main()."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        os.makedirs("anchors", exist_ok=True)
        for s in existing_anchor_seqs:
            fetch_anchors.write_json(
                f"anchors/{s:06d}.json",
                {k: _anchor(s, _ts(1))[k] for k in fetch_anchors.PUBLIC_FIELDS})
        if latest_json is not None:
            fetch_anchors.write_json("latest.json", latest_json)
        return fetch_anchors.main()
    finally:
        os.chdir(cwd)


def _read(tmp_path, rel):
    p = os.path.join(tmp_path, rel)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


# --------------------------------------------------------------------------- #

def test_fresh(tmp_path):
    """Empty repo, spine at seq 1, fresh, no discrepancy -> writes & exits 0."""
    _install_spine({1: _anchor(1, _ts(1))})
    rc = _run_in(tmp_path)
    assert rc == 0
    assert _read(tmp_path, "anchors/000001.json")["seq"] == 1
    assert _read(tmp_path, "latest.json")["seq"] == 1


def test_catch_up(tmp_path):
    """Repo at seq 1, spine at seq 3 -> writes 2 and 3 in order, exits 0."""
    _install_spine({s: _anchor(s, _ts(1)) for s in (1, 2, 3)})
    rc = _run_in(tmp_path, existing_anchor_seqs=(1,))
    assert rc == 0
    assert _read(tmp_path, "anchors/000002.json")["seq"] == 2
    assert _read(tmp_path, "anchors/000003.json")["seq"] == 3
    assert _read(tmp_path, "latest.json")["seq"] == 3


def test_stale(tmp_path):
    """Newest anchor older than the 26h floor -> exits 3, writes nothing."""
    _install_spine({1: _anchor(1, _ts(30))})
    rc = _run_in(tmp_path)
    assert rc == 3
    assert _read(tmp_path, "anchors/000001.json") is None


def test_discrepancy(tmp_path):
    """A fetched anchor carrying discrepancy=true -> exits 4, writes nothing."""
    _install_spine({1: _anchor(1, _ts(1)),
                    2: _anchor(2, _ts(1), discrepancy=True)})
    rc = _run_in(tmp_path, existing_anchor_seqs=(1,))
    assert rc == 4
    assert _read(tmp_path, "anchors/000002.json") is None


def test_gap(tmp_path):
    """A hole in the seq series on the spine -> exits 5, writes nothing."""
    # spine latest is seq 3 but seq 2 is missing.
    _install_spine({1: _anchor(1, _ts(1)), 3: _anchor(3, _ts(1))})
    rc = _run_in(tmp_path, existing_anchor_seqs=(1,))
    assert rc == 5
    assert _read(tmp_path, "anchors/000003.json") is None


def test_noop(tmp_path):
    """Repo already at the spine's latest seq, fresh -> exits 0, no new files,
    latest.json untouched (=> no commit)."""
    latest = _anchor(1, _ts(1))
    _install_spine({1: latest})
    existing_latest = {k: latest[k] for k in fetch_anchors.LATEST_FIELDS}
    rc = _run_in(tmp_path, existing_anchor_seqs=(1,), latest_json=existing_latest)
    assert rc == 0
    # no seq 2 appeared, and latest.json is byte-for-byte unchanged.
    assert _read(tmp_path, "anchors/000002.json") is None
    assert _read(tmp_path, "latest.json") == existing_latest


def test_noop_resyncs_drifted_latest(tmp_path):
    """No new anchors but latest.json missing/drifted -> rewritten, still 0."""
    latest = _anchor(1, _ts(1))
    _install_spine({1: latest})
    rc = _run_in(tmp_path, existing_anchor_seqs=(1,), latest_json=None)
    assert rc == 0
    assert _read(tmp_path, "latest.json")["seq"] == 1


# --------------------------------------------------------------------------- #

def _main():
    import tempfile
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        with tempfile.TemporaryDirectory() as d:
            try:
                t(d)
                print(f"PASS {t.__name__}")
            except Exception:
                failures += 1
                print(f"FAIL {t.__name__}")
                traceback.print_exc()
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_main())
