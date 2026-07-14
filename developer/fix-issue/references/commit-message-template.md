# Commit Message Template

- Keep the commit message short and descriptive.
- Commit messages survive the code changes.
- The commit message must have enough information to understand the change.
- The commit message must be descriptive enough for manual code version bisect in case of a regression / revert.

Use this structure:

```markdown
<Descriptive title without the issue number as the first line>

<What was decided and why. This could be a summarization of the "summary" section of the issue report.>

**Changes**

<Bulleted list of the changes.>

**Tests**

<If applicable, instructions for manual verification (how to run the tests, etc.)>

<If applicable, "Fixes #NUM" as the last line>
```
