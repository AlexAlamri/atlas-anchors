# atlas-anchors

Public, tamper-evident **integrity anchors** for the Atlas event log.

Atlas keeps an append-only log of events in a private Postgres (Supabase) spine.
This repository publishes, once a day, a cryptographic **head** over that log
plus an independent **OpenTimestamps** proof of when that head existed. Anyone
can use these to check that the private log has not been silently rewritten —
**without ever seeing its contents**.

This repo contains **heads and proofs only**. It never contains event bodies,
titles, `meta`, activity timestamps, or any private-spine content. That is a
hard rule, mechanically enforced by [`scripts/guard.sh`](scripts/guard.sh) on
every commit.

---

## What is published

| Path | What it is |
|------|------------|
| `anchors/NNNNNN.json` | one anchor: the public fields of a single chain step |
| `anchors/NNNNNN.json.ots` | the OpenTimestamps proof for that anchor file |
| `artefacts/<date>-<label>.json` | a deliberately-registered external artefact digest (sha256 + label) |
| `artefacts/<date>-<label>.json.ots` | its OpenTimestamps proof |
| `latest.json` | a pointer to the newest anchor (public fields, no `batch_hash`) |

An **anchor** is one row of the public surface:

```json
{
  "seq": 1,
  "computed_at": "2026-07-22T22:26:33.361496+00:00",
  "new_count": 91,
  "total_count": 91,
  "batch_hash": "8ed59844aef815c5d84f41ba6704bce47565768b9b58b2e2a3fbbb6bfa0696d8",
  "prev_head": "e16ef2c83e74753237fe326f57acd704ec764b7148bdf49901ce439a380cdb79",
  "head": "9509be07bb1bdc32f31743aab137e4a5c77d9083697985a2de758598777bfbc1",
  "algo": "v1",
  "discrepancy": false
}
```

`prev_head` of anchor 1 is `head_0 = SHA-256("atlas-anchors-v1")`.

`covered_through` (the time of the last folded event) is deliberately **not**
published — it would leak activity timing. It exists only in the private table.

---

## The frozen v1 algorithm

`v1` is a **consensus rule**. It is **immutable**: once anchor 1 exists, the way
`v1` heads are computed can never change. Any future change is a **parallel v2**
with its own genesis. The canonical implementation is the SQL published by the
spine (`public.anchor_rowhash_v1`, `public.record_anchor`); this text is the
human-readable statement of that same rule.

**Scope.** All rows of the private `events` table for the single study user.
`user_id` is **excluded** from every hash.

**Canonical order.** `created_at ASC, id ASC`. (Writers never set `created_at`;
it is the database default at insert and is never updated. `occurred_at` carries
event-time semantics and is a separate, hashed field.)

**Timestamp rendering.** Every timestamp is rendered as
`to_char(x at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"')`
— e.g. `2026-06-28T23:19:37.153166Z`. This is independent of any session
timezone or datestyle setting. A `timestamptz` is **never** rendered with
`::text`.

**Row hash.** For each event, `rowhash` is the SHA-256 of the UTF-8 encoding of
these 11 fields, in this order, joined by the unit-separator byte `chr(31)`:

1. `id::text`
2. `spoke_id`
3. `kind`
4. `coalesce(title,'')`
5. `coalesce(body,'')`
6. `source`
7. `coalesce(confidence,'')`
8. `coalesce(external_id,'')`
9. `meta::text`  *(PostgreSQL's canonical `jsonb` text rendering — sorted keys, normalised whitespace)*
10. `occurred_at`  *(rendered as above)*
11. `created_at`  *(rendered as above)*

`rowhash` is expressed as lowercase hex.

**Batching by cumulative count.** Let `total_n` be the number of canonical rows
at anchor `n`, and `total_0 = 0`. Batch `n` is the rows whose 1-based position in
canonical order lies in the half-open interval `(total_{n-1}, total_n]`.

`batch_hash_n` = SHA-256 of the concatenation of the batch's lowercase-hex
`rowhash` values, in canonical order, **with no separator**. An empty batch
(`new_count = 0`) has `batch_hash = SHA-256("")` =
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

**Chain.**

```
head_0 = SHA-256("atlas-anchors-v1")
head_n = SHA-256( head_{n-1}_hex  ||  batch_hash_n_hex )      // ASCII lowercase-hex concatenation
```

`head_0` = SHA-256 of the ASCII string `atlas-anchors-v1` =
`e16ef2c83e74753237fe326f57acd704ec764b7148bdf49901ce439a380cdb79`.

**Self-check (every run).** Before recording a new anchor, the spine recomputes
every `rowhash` from the current log and refolds the chain from `head_0` using
the **stored** batch sizes, comparing each recomputed head to the stored head.
Any mismatch sets `discrepancy = true` (with a note) on the newly recorded
anchor — the new batch is **still recorded**. A `true` here means the historical
log no longer reproduces a previously-published head: evidence of tampering,
deletion, reordering, or a mutated field in already-anchored history.

---

## How to verify

You need only this repository and (for stronger claims) read access to the
private log. **The canonical verifier is the published SQL run inside
PostgreSQL**, because `meta::text` must use PostgreSQL's own `jsonb` rendering;
a re-implementation in another language must reproduce that rendering exactly.

### 1. Chain continuity (needs only this repo)

For every consecutive pair of anchors, check
`head_n == SHA-256(prev_head_n_hex || batch_hash_n_hex)` and that
`prev_head_n == head_{n-1}`. This proves the published series is internally
consistent and append-only. It does **not**, by itself, prove anything about the
private rows — for that, see (2) and (3).

### 2. Full-log recompute (needs read access to the private log)

Run the published `v1` SQL over the private `events` table. Recompute every
`rowhash`, refold from `head_0` using each anchor's `total_count` as the batch
boundary, and confirm every recomputed `head` equals the published `head`. If
all match, the private log is exactly the log that produced this public chain.
Any `discrepancy = true` anchor, or any mismatch, localises tampering to a batch.

### 3. Single-event inclusion proof

To prove one specific event is folded into the chain **without revealing the
rest of the log**, the holder of the private log discloses, for that event:

* the event's **canonical byte string** (the exact `chr(31)`-joined field string
  hashed to produce its `rowhash`), from which anyone recomputes its `rowhash`;
* the ordered **vector of `rowhash` values** for that event's batch (hashes
  only — no bodies), from which anyone recomputes that batch's `batch_hash`;
* the **public anchor series** in this repo.

A verifier then confirms the recomputed `batch_hash` matches the published
`batch_hash` for that `seq`, and that the chain folds to the published `head`.
This shows the event was present when that anchor was stamped, while every other
event is disclosed only as an opaque hash.

### 4. Timestamp proof (needs only this repo)

`ots verify anchors/NNNNNN.json.ots` confirms, against the Bitcoin blockchain,
that `anchors/NNNNNN.json` existed no later than the attested time. `ots info`
shows a pending or complete attestation for every committed anchor.

---

## What is and is not proven

**Proven**

* **Append-only integrity from anchor 1 onward.** Once an anchor is published and
  stamped, the private log cannot be edited, reordered, or truncated in the
  anchored range without the next self-check raising `discrepancy` and the
  recompute in (2) failing.
* **An upper bound on each anchor's date.** The OTS proof shows the head — and
  therefore the log content it commits to — existed no later than the stamp.
* **Inclusion** of any disclosed event (via 3), and **exact reproduction** of the
  whole log (via 2), for holders of the private data.

**Not proven**

* **Not** that any event is *true*, accurate, or authored by anyone in
  particular. An anchor commits to *what the log said*, not to *reality*.
* **Not** a *lower* bound on dates: nothing here prevents backdating a
  `occurred_at` value *before* it was first anchored. Anchoring only fixes state
  *going forward* from each stamp.
* **Nothing about the pre-anchor window** beyond what anchor 1 folds in (below).
* **Not** confidentiality of disclosed events: an inclusion proof (3) reveals the
  disclosed event's full canonical fields to whoever receives the proof.

---

## Pre-anchor gap disclosure

Anchoring began on **2026-07-22** with **anchor 1** (`seq 1`,
`head 9509be07…bfbc1`, `total_count 91`). Anchor 1's batch folds in the **entire
pre-existing log**, from the earliest event (**2026-06-28**) through
`covered_through`. That includes the spine governance decisions pinned on
**16 July 2026** (`bd32a523`, `a5bb5bea`, `27aca70d`, `0aa68bd4`, `63050c75`).

Those pre-anchor rows are covered by the chain **from anchor 1 forward**, but
they carry **no independent timestamp proof of their state before anchor 1**.
The OTS proof on anchor 1 establishes only that the log had exactly this content
**no later than** anchor 1's stamp; it cannot establish any earlier date for the
16 July pins or any other pre-anchor row. Continuous, per-day forward integrity
begins at anchor 1.

---

## Redaction and epoch protocol (hub decision D-A, canonical)

The event log is append-only. Corrections are always new corrective events,
never in-place edits. There is no supported path for editing or deleting an
event during normal operation. During a study observation window, deletion is
prohibited outright.

If a deletion is ever forced outside that constraint (realistically only to
remove identifiable or clinical-adjacent content that reached the log in error,
hazard H8), it is performed as an explicit, disclosed epoch break, never a
silent removal:

1. The offending row(s) are deleted.
2. A corrective `hub:deviation:*` event is written stating what category of
   content was removed and why, never reproducing the content.
3. A dated epoch-break note is added to this repository recording the seq at
   which the break occurs.

The anchor chain makes this tamper-evident by construction. Because batching
runs over the canonical row order by cumulative count, deleting any row shifts
every later batch and diverges every subsequent head. The next nightly
self-check recomputes from genesis and sets `discrepancy = true`; this
divergence is the intended evidence of the redaction, not a fault.

Verification across an epoch break: anchors committed before the break are
immutable in this repository and OpenTimestamps-stamped, so they continue to
attest, in hash form, that the redacted event existed before the break; its
removal cannot be un-happened. Pre-break events verify against the pre-break
anchor series; events after the break verify against the post-break series.
The README names the break seq so a verifier reads the head discontinuity as
the documented redaction rather than tampering.

---

## Surface policy (what may ever land here)

Only these may be committed, and `scripts/guard.sh` enforces it mechanically:

* `anchors/*.json` — the nine public anchor fields, nothing else, ≤ 2 KB, flat.
* `anchors/*.json.ots`, `artefacts/*.json.ots` — OpenTimestamps proofs.
* `artefacts/*.json` — `{sha256, label, computed_at}` only, ≤ 2 KB, flat.
* `latest.json` — public anchor fields (no `batch_hash`).
* `README.md`, `.github/**`, `scripts/**`.

Any other path, any JSON key outside the allowed set, any `body`/`title`/`meta`
(or other private) key at any depth, any nested object, or any file over 2 KB
**fails the commit**. A red `anchor` workflow run on a stale or discrepant
anchor is the pre-agreed **H4 alert floor** — it is *meant* to page.

---

## Layout

```
anchors/      NNNNNN.json + .json.ots      one per chain step
artefacts/    <date>-<label>.json + .ots   deliberate external digests (D-B)
latest.json                                pointer to the newest anchor
scripts/
  guard.sh            surface-policy guard (+ --selftest)
  fetch_anchors.py    read RPC, materialise anchors, freshness/discrepancy gates
  make_artefact.py    D-B artefact recorder
.github/workflows/
  anchor.yml          nightly read → stamp → guard → commit (03:15 UTC)
README.md
```
