#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER="$ROOT/scripts/install-skills"
TEST_ROOT="$(mktemp -d)"
trap 'rm -r "$TEST_ROOT"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_skill_installed() {
  local root="$1"
  [[ -f "$root/fix-issue/SKILL.md" ]] || fail "expected fix-issue under $root"
}

HOME="$TEST_ROOT/codex-home" "$INSTALLER" developer/fix-issue >/dev/null
assert_skill_installed "$TEST_ROOT/codex-home/.agents/skills"

HOME="$TEST_ROOT/claude-home" "$INSTALLER" --target claude developer/fix-issue >/dev/null
assert_skill_installed "$TEST_ROOT/claude-home/.claude/skills"

HOME="$TEST_ROOT/opencode-home" XDG_CONFIG_HOME="$TEST_ROOT/xdg" \
  "$INSTALLER" --target opencode developer/fix-issue >/dev/null
assert_skill_installed "$TEST_ROOT/xdg/opencode/skills"

HOME="$TEST_ROOT/opencode-default-home" env -u XDG_CONFIG_HOME \
  "$INSTALLER" --target opencode developer/fix-issue >/dev/null
assert_skill_installed "$TEST_ROOT/opencode-default-home/.config/opencode/skills"

CUSTOM_DEST="$TEST_ROOT/custom-skills"
"$INSTALLER" --target opencode --dest "$CUSTOM_DEST" developer/fix-issue >/dev/null
assert_skill_installed "$CUSTOM_DEST"

DRY_RUN_DEST="$TEST_ROOT/dry-run-skills"
dry_run_output="$("$INSTALLER" --target opencode --dest "$DRY_RUN_DEST" --dry-run developer/fix-issue)"
[[ "$dry_run_output" == *"would install"* ]] || fail "expected dry-run install preview"
[[ ! -e "$DRY_RUN_DEST" ]] || fail "dry-run created destination $DRY_RUN_DEST"

if "$INSTALLER" --target unsupported --dest "$TEST_ROOT/invalid" developer/fix-issue \
  >"$TEST_ROOT/invalid.out" 2>"$TEST_ROOT/invalid.err"; then
  fail "unsupported target unexpectedly succeeded"
fi
grep -q "codex, claude, or opencode" "$TEST_ROOT/invalid.err" \
  || fail "unsupported target error did not list valid targets"

echo "install-skills tests passed"
