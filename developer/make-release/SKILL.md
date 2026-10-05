---
name: make-release
description: "Draft release notes and create a local annotated Git release tag after user review. Use when preparing a release tag, with an optional tag name and additional instructions."
---

# Make Release

Prepare an annotated tag on the current repository's HEAD with a user-approved message suitable for a later `gh release create TAG --notes-from-tag`. This skill creates the tag locally; pushing tags and creating GitHub releases require separate user instructions.

## Arguments

The first argument may be a tag ref name, such as `v1.2.4`. Remaining text supplies additional instructions. If no tag name is supplied, infer it as described below. Additional user instructions take priority over this skill's defaults and rules; do not interpret descriptive text as a tag name.

## Preflight and Tag Name

1. Find the current repository root with `git rev-parse --show-toplevel` and run subsequent Git commands there. Run `git status --short --untracked-files=all`. If staged, unstaged, or untracked changes exist, report them and stop tag creation. Do not commit, stash, clean, or discard them to continue.
2. Record HEAD's commit SHA. List local tags with `git tag --list` and remote tags with `git ls-remote --tags origin`. If origin is missing or the remote lookup fails, report the failure and stop; local absence does not establish remote availability. Do not change remotes or authentication.
3. For an explicit tag name, validate it with `git check-ref-format "refs/tags/$TAG"` and reject names beginning with `-`. Compare the exact name against local tags and remote `refs/tags/NAME` entries, accounting for peeled annotated-tag entries ending in `^{}`. Do not use a substring or glob match to determine existence. If it exists in either location, stop and ask the user for a new name or to delete the existing tag. Do not delete or overwrite it yourself.
4. Without a name, choose the highest stable numeric `MAJOR.MINOR.PATCH` version across local and origin tags, accepting an optional `v` prefix. Compare version components numerically rather than lexicographically or by tag date. Preserve that tag's prefix and increment PATCH: `v1.2.3` becomes `v1.2.4`. This default is a patch bump. Ignore prerelease and non-version tags for this inference. If there is no stable version or the naming scheme is ambiguous, ask for a tag name. Apply the same validation and collision checks to the inferred name.

## Draft the Message

Read `.github/RELEASE_TAG_TEMPLATE.md` in the target repository if it exists. Otherwise, read this skill's bundled [references/tag-body-template.md](references/tag-body-template.md), resolved relative to the installed skill directory. Follow the selected template's structure and any additional user instructions.

Choose the previous release tag reachable from the recorded HEAD as the comparison baseline, following the repository's release conventions. Inspect the commits and relevant changes since that baseline with `git log` and `git diff`. Explain the chosen baseline; do not silently treat unavailable history as an empty release. If a needed remote tag is absent locally, fetch only the required tag when safe, then inspect it. If fetching or reading history fails, stop and report the error. For a confirmed first release, summarize the history through the recorded HEAD.

Write evidence-backed, user-facing notes. Highlight meaningful features, fixes, breaking changes, and migration steps when present. Omit empty optional sections and replace all template placeholders. Do not invent verification results, issue links, compatibility claims, or contributors. Mention test results only when supported by inspected evidence or checks actually run.

Present the proposed tag name, target commit, comparison baseline, template source, and complete tag message for review. Ask the user to approve the message before creating the tag. Wait for approval; requesting edits is not approval. Incorporate edits and present the revised message for approval when its contents change.

Keep any draft file outside the repository, such as in a temporary directory, so drafting does not dirty the worktree. Preserve the exact approved message as UTF-8 text in a file rather than interpolating it into a shell command.

## Create the Local Tag

After approval, recheck Git status, HEAD, and both local and origin tag names. Stop if changes appeared or the name now exists. If HEAD changed, regenerate the draft for the new commit and request approval again. If any required check fails, report the error and leave the tag uncreated.

Create the annotated tag at the approved commit using safely quoted arguments and the approved message file:

```bash
git tag -a --cleanup=verbatim -F "$MESSAGE_FILE" "$TAG" "$APPROVED_COMMIT"
```

Do not use `-f`. If tag creation fails, report the error without deleting, replacing, or retrying an existing tag. Verify that `refs/tags/TAG` is an annotated tag, that its peeled commit equals the approved SHA, and that its annotation contains the approved message using `git cat-file -t`, `git rev-parse`, and `git cat-file -p`. If verification fails, report the discrepancy and leave the tag for user review.

Report the created tag name, target commit, and verification result. Make clear that the tag is local and whether anything remains unresolved. Do not push or publish as part of this workflow.
