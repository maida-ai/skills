# Commit Message Template

- Keep the commit message short and descriptive.
- Commit messages survive the code changes.
- The commit message must have enough information to understand the change.
- The commit message must be descriptive enough for manual code version bisect in case of a regression / revert.

Use this structure for every commit. Replace all placeholders with real content.
Keep both sections, even for a small change:

```markdown
<Descriptive title without the issue number as the first line>

<One or two sentences explaining what was decided and why.>

**Changes**

- <Key change and its purpose.>

**Tests**

- `<Command actually run>` — <result>.

Closes #<ISSUE>
```

If no check ran, write `- Not run: <reason>` under `**Tests**`.
For multiple commits on one issue branch, omit the closing line from all but
the final, top commit. Each subissue branch closes only its own issue; the parent
branch closes the parent in its own final commit. A necessary prerequisite
commit in another repository may end with `Refs OWNER/REPO#<ISSUE>` for
traceability, but that line is not a closing keyword and never substitutes for
the final `Closes` line in the issue's repository. Never add a closing keyword
for an issue marked `[skipped]` or `[need-feedback]`, or create an empty commit
just to add one. GitHub processes the closing keyword when the completed commit
reaches the issue repository's default branch; a local commit does not close it.
