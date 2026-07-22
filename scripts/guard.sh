#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# guard.sh — public-surface guard for the atlas-anchors evidence repo.
#
# The spine publishes HEADS and PROOFS only, never event bodies. This guard is
# the mechanical enforcement of that rule: it refuses to let the workflow commit
# anything outside the allowed surface. It is the last line before `git commit`.
#
# It FAILS (exit 1) if any STAGED file:
#   * has a path outside the whitelist
#       anchors/*.json  anchors/*.json.ots
#       artefacts/*.json  artefacts/*.json.ots
#       latest.json  README.md  .github/**  scripts/**
#   * is a *.json (not *.json.ots) whose top-level keys fall outside the allowed
#     set for its class (anchor / latest / artefact)
#   * is a *.json containing — at ANY depth — a forbidden key
#       (body, title, meta, covered_through, occurred_at, external_id, user_id)
#   * is a *.json larger than 2048 bytes, is not a flat object, or holds any
#     nested object/array (which could smuggle a body)
#
# Usage:
#   scripts/guard.sh              check the git staging area (git diff --cached)
#   scripts/guard.sh --selftest   exercise the guard logic on fixtures (no repo)
# ---------------------------------------------------------------------------
set -euo pipefail

MAX_JSON_BYTES=2048

err() { echo "GUARD FAIL: $*" >&2; }

# path_allowed <path>  -> 0 if the path is inside the published surface
# (case patterns: '*' spans '/', which is what we want for .github/** & scripts/**)
path_allowed() {
  case "$1" in
    anchors/*.json.ots|artefacts/*.json.ots) return 0 ;;
    anchors/*.json|artefacts/*.json)         return 0 ;;
    latest.json|README.md)                   return 0 ;;
    .github/*|scripts/*)                      return 0 ;;
    *) return 1 ;;
  esac
}

# check_json <path> <class:anchor|latest|artefact>
check_json() {
  python3 - "$1" "$2" "$MAX_JSON_BYTES" <<'PY'
import json, sys
path, cls, maxb = sys.argv[1], sys.argv[2], int(sys.argv[3])

ALLOWED = {
    "anchor":   {"seq","computed_at","new_count","total_count",
                 "batch_hash","prev_head","head","algo","discrepancy"},
    "latest":   {"seq","computed_at","new_count","total_count",
                 "prev_head","head","algo","discrepancy"},
    "artefact": {"sha256","label","computed_at"},
}[cls]
FORBIDDEN = {"body","title","meta","covered_through",
             "occurred_at","external_id","user_id"}

raw = open(path, "rb").read()
if len(raw) > maxb:
    print(f"{path}: {len(raw)} bytes > {maxb} limit"); sys.exit(1)
try:
    doc = json.loads(raw)
except Exception as e:
    print(f"{path}: invalid JSON: {e}"); sys.exit(1)
if not isinstance(doc, dict):
    print(f"{path}: top-level JSON must be an object"); sys.exit(1)

def all_keys(o):
    ks = set()
    if isinstance(o, dict):
        for k, v in o.items():
            ks.add(k); ks |= all_keys(v)
    elif isinstance(o, list):
        for v in o: ks |= all_keys(v)
    return ks

hit = all_keys(doc) & FORBIDDEN
if hit:
    print(f"{path}: forbidden key(s) present: {sorted(hit)}"); sys.exit(1)

extra = set(doc.keys()) - ALLOWED
if extra:
    print(f"{path}: key(s) outside allowed '{cls}' set: {sorted(extra)}"); sys.exit(1)

for k, v in doc.items():
    if isinstance(v, (dict, list)):
        print(f"{path}: value for '{k}' must be scalar (no nested object/array)"); sys.exit(1)

sys.exit(0)
PY
}

check_staged() {
  local files fail=0 n=0
  files="$(git diff --cached --name-only --diff-filter=ACMR)"
  if [ -z "$files" ]; then echo "guard: no staged files to check"; return 0; fi
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    n=$((n+1))
    if ! path_allowed "$p"; then err "path not in whitelist: $p"; fail=1; continue; fi
    case "$p" in
      *.json.ots)       : ;;                                   # binary proof: no key/size check
      anchors/*.json)   check_json "$p" anchor   || fail=1 ;;
      artefacts/*.json) check_json "$p" artefact || fail=1 ;;
      latest.json)      check_json "$p" latest   || fail=1 ;;
      *)                : ;;                                   # README.md / .github/** / scripts/**
    esac
  done <<EOF
$files
EOF
  if [ "$fail" -ne 0 ]; then err "staged tree violates the public-surface policy"; return 1; fi
  echo "guard: OK — $n staged path(s) within surface policy"
}

selftest() {
  local tmp rc=0; tmp="$(mktemp -d)"
  # --- paths ---
  path_allowed "anchors/000001.json"            || { echo "selftest: good anchor path rejected"; rc=1; }
  path_allowed "anchors/000001.json.ots"        || { echo "selftest: good ots path rejected"; rc=1; }
  path_allowed "artefacts/2026-07-22-osf.json"  || { echo "selftest: good artefact path rejected"; rc=1; }
  path_allowed "latest.json"                    || { echo "selftest: latest.json rejected"; rc=1; }
  path_allowed ".github/workflows/anchor.yml"   || { echo "selftest: .github path rejected"; rc=1; }
  path_allowed "scripts/guard.sh"               || { echo "selftest: scripts path rejected"; rc=1; }
  if path_allowed "secrets.env";      then echo "selftest: root path allowed (bad)"; rc=1; fi
  if path_allowed "evil.json";        then echo "selftest: root json allowed (bad)"; rc=1; fi
  if path_allowed "latest.json.ots";  then echo "selftest: stray ots allowed (bad)"; rc=1; fi
  # --- json content ---
  cat > "$tmp/good.json" <<'J'
{"seq":1,"computed_at":"2026-07-22T02:45:00.000000Z","new_count":90,"total_count":90,"batch_hash":"aa","prev_head":"bb","head":"cc","algo":"v1","discrepancy":false}
J
  check_json "$tmp/good.json" anchor            || { echo "selftest: good anchor rejected"; rc=1; }
  echo '{"seq":1,"algo":"v1","body":"secret"}'          > "$tmp/f1.json"
  echo '{"seq":1,"algo":"v1","surprise":"x"}'           > "$tmp/f2.json"
  echo '{"seq":1,"algo":"v1","meta":{"x":1}}'           > "$tmp/f3.json"
  echo '{"seq":1,"algo":"v1","head":{"body":"x"}}'      > "$tmp/f4.json"
  python3 -c "import json;print(json.dumps({'seq':1,'algo':'v1','head':'a'*4000}))" > "$tmp/f5.json"
  for bad in f1 f2 f3 f4 f5; do
    if check_json "$tmp/$bad.json" anchor 2>/dev/null; then
      echo "selftest: bad fixture $bad accepted (should fail)"; rc=1; fi
  done
  # artefact happy path
  echo '{"sha256":"deadbeef","label":"osf-reg","computed_at":"2026-07-22T00:00:00.000000Z"}' > "$tmp/art.json"
  check_json "$tmp/art.json" artefact           || { echo "selftest: good artefact rejected"; rc=1; }
  rm -rf "$tmp"
  if [ "$rc" -eq 0 ]; then echo "guard selftest: PASS"; return 0; fi
  echo "guard selftest: FAIL"; return 1
}

case "${1:-check}" in
  --selftest|selftest) selftest ;;
  check|"")            check_staged ;;
  *) echo "usage: guard.sh [--selftest]" >&2; exit 2 ;;
esac
