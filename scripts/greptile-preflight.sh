#!/usr/bin/env bash
# GENERATED FILE. Canonical source: algominds-ai/algominds-standards
# -> greptile/greptile-preflight.sh. Edit there, then run greptile/sync-greptile.sh.
#
# The free gate. Everything here costs zero Greptile credits, so it runs BEFORE a PR
# leaves draft and before /greploop is allowed to spend one.
#
#   bash scripts/greptile-preflight.sh              # diff vs the default branch
#   bash scripts/greptile-preflight.sh origin/main  # diff vs an explicit base
#
# Exit 0 means the PR is allowed to go ready-for-review. Anything else means fix it
# locally, because a Greptile round that reports a type error is a credit spent on
# something the linter catches for nothing.
#
# Detects the stack from what is on disk and runs that stack's own CI checks:
#   Node        package.json scripts + Biome/copy rules on the diff
#   Python      poetry: black, flake8, mypy, pytest  (mirrors gainz backend tests.yml)
#   Dart        flutter/dart analyze + test
# A repo can be more than one. Anything not present is skipped, not failed: a gate that
# red-lights a repo that never had that tool just trains people to switch it off.

set -uo pipefail

BASE="${1:-}"
if [ -z "$BASE" ]; then
  for b in origin/main origin/master main master; do
    git rev-parse --verify "$b" >/dev/null 2>&1 && { BASE="$b"; break; }
  done
fi
[ -n "$BASE" ] || { echo "preflight: cannot resolve a base branch"; exit 1; }

fail=0
ran=0
skipped=()

run_step() {
  local label="$1"; shift
  printf '  %-26s ' "$label"
  local out
  if out=$("$@" 2>&1); then
    echo "ok"; ran=$((ran + 1))
  else
    echo "FAIL"
    echo "$out" | tail -n 40 | sed 's/^/      /'
    fail=1; ran=$((ran + 1))
  fi
}

have() { command -v "$1" >/dev/null 2>&1; }

echo "Greptile preflight, diffing against $BASE"

# ---------------------------------------------------------------- Node
if [ -f package.json ]; then
  if   [ -f pnpm-lock.yaml ]; then PM=pnpm
  elif [ -f yarn.lock ];      then PM=yarn
  elif [ -f bun.lockb ];      then PM=bun
  else                             PM=npm
  fi
  echo; echo "node ($PM)"
  has_script() { node -e "process.exit(require('./package.json').scripts?.['$1']?0:1)" 2>/dev/null; }
  for s in typecheck lint test build; do
    if has_script "$s"; then run_step "$s" "$PM" run "$s"; else skipped+=("node: $s (no script)"); fi
  done
fi

# ------------------------------------------------------- Python (poetry)
if [ -f pyproject.toml ]; then
  echo; echo "python"
  if have poetry; then
    R=(poetry run)
  else
    R=()
    skipped+=("python: poetry not installed, running tools directly")
  fi
  # Mirrors the jobs in gainz backend .github/workflows/tests.yml. If CI runs it, the
  # gate runs it, so you find out here instead of after the PR is already open.
  for pair in "black:black --check ." "flake8:flake8 --count ." "mypy:mypy ." "pytest:pytest -q"; do
    tool="${pair%%:*}"; cmd="${pair#*:}"
    if [ "$tool" = "flake8" ] && [ ! -f .flake8 ] && ! grep -q "\[flake8\]" setup.cfg tox.ini 2>/dev/null; then
      skipped+=("python: flake8 (not configured)"); continue
    fi
    if [ "$tool" = "mypy" ] && [ ! -f mypy.ini ] && ! grep -q "\[tool.mypy\]" pyproject.toml 2>/dev/null; then
      skipped+=("python: mypy (not configured)"); continue
    fi
    if [ ${#R[@]} -eq 0 ] && ! have "$tool"; then
      skipped+=("python: $tool (not installed)"); continue
    fi
    # shellcheck disable=SC2086
    run_step "$tool" "${R[@]}" $cmd
  done
fi

# --------------------------------------------------------------- Dart
if [ -f pubspec.yaml ]; then
  echo; echo "dart"
  if have flutter; then D=flutter; elif have dart; then D=dart; else D=""; fi
  if [ -z "$D" ]; then
    skipped+=("dart: neither flutter nor dart on PATH")
  else
    run_step "analyze" "$D" analyze
    if [ -d test ]; then run_step "test" "$D" test; else skipped+=("dart: test (no test/ dir)"); fi
  fi
fi

# ------------------------------------------- Algominds shared standards
# These gate the DIFF, not the repo, so pre-existing debt does not block an unrelated
# PR. Same contract as the CI job in ci-snippet.yml.
if [ -f scripts/biome-changed.sh ] || [ -f scripts/check-copy-rules.sh ]; then
  echo; echo "standards"
  [ -f scripts/biome-changed.sh ] \
    && run_step "biome (changed)" bash scripts/biome-changed.sh "$BASE" \
    || skipped+=("standards: biome-changed.sh (not synced)")
  [ -f scripts/check-copy-rules.sh ] \
    && run_step "copy rules (changed)" bash scripts/check-copy-rules.sh --changed "$BASE" \
    || skipped+=("standards: check-copy-rules.sh (not synced)")
fi

echo
if [ ${#skipped[@]} -gt 0 ]; then
  echo "skipped:"
  printf '  - %s\n' "${skipped[@]}"
  echo
fi

if [ "$fail" -ne 0 ]; then
  cat <<'MSG'
PREFLIGHT RED. Do not mark the PR ready for review and do not run /greploop.
Every finding above is one Greptile would charge a credit to tell you about.
MSG
  exit 1
fi

# A gate that checked nothing and said "green" is worse than no gate, because it is the
# one people trust. Say so instead.
if [ "$ran" -eq 0 ]; then
  cat <<'MSG'
PREFLIGHT RAN NOTHING. No stack was detected and no checks executed, so this is not a
pass. Either the toolchain is missing from this machine or the repo needs its checks
wired up. Do not treat this as permission to spend a credit.
MSG
  exit 2
fi

cat <<MSG
PREFLIGHT GREEN ($ran checks).

Next, still free:
  /code-review high        (Claude tokens, not Greptile credits)

Then, and only then, mark the PR ready for review. That is the moment it costs a
credit. /greploop after that, capped at 2 rounds.
MSG
