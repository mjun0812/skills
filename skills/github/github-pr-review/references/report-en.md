# <reviewer-name> PR Review

<!--
Authoring rules:
- Summary describes only what the PR changes, in 1-2 sentences. Do not summarize the review result or finding counts.
- If CI has failing checks, or the Contract axis was skipped, add one line for each to the Summary.
- Findings only contains findings from the Finder, Standards, and Contract SubAgent that the verifier judged confirmed.
- Findings from the Standards and Contract SubAgent also block merge and affect the Verdict.
- If Findings has no items, keep the heading and write "N/A".
- Separate findings with a `### N. [Category] Summary` heading each. List Finder findings first, Standards findings second, and Contract findings third, numbering all Findings sequentially from 1.
- Category is a short label describing the main harm or kind.
- Summary states only the harm in one sentence; the cause belongs in `Problem`.
- Bold each field name on its own line and start its content on the next line. Separate fields with a blank line.
- Each Finder finding must include `Location` / `Problem` / `Execution path` / `Completion condition`.
- Each Standards or Contract finding must include `Location` / `Problem` / `Basis` / `Completion condition`.
- Add `Other locations` and `Notes` before `Completion condition` only when they apply.
- A Finder finding's `Problem` states only the triggering condition, cause, and concrete harm in one paragraph of at most three sentences.
- A Standards finding's `Problem` combines the facts visible in the diff and why deferring it until after merge is unsafe.
- A Contract finding's `Problem` combines the current state of the implementation and how it diverges from the contract's promise.
- `Execution path` is a numbered list tracing the runtime path that reaches the problem, one `file:line` (note) hop per line.
- `Basis` is a bullet list; for a Contract finding it quotes the relevant spec statement and cites the implementation `file:line`.
- `Other locations` is a bullet list of other `file:line` that share the same problem, one per line.
- `Notes` is a bullet list of facts that are not the core problem but help judgment, such as comparisons with the pre-change behavior or the precedent.
- `Completion condition` is a bullet list of states that demonstrate the problem is resolved, one sentence per condition, not an implementation method. Add one supplementary sentence on the next line only when needed.
- Do not include the Finder's and verifier's raw `Evidence` or verification logs in the review body or inline comments. Present reachability as a polished `Execution path`.
- Do not create finding sections other than Findings in the final review.
- Only Findings become inline comments.
-->

## Summary

<!-- 1-2 sentence summary of what this PR changes -->

## Verdict

<!-- APPROVE or REQUEST_CHANGES -->

## Findings

<!-- Findings from the Finder -->

### 1. [Category] Summary

**Location**: `filename:line`

**Problem**:
...

**Execution path**:

1. `file:line` (note)
2. `file:line` (note)

**Other locations**:

- `file:line`

**Notes**:

- ...

**Completion condition**:

- ...
- ...

<!-- Findings from the Standards SubAgent. They are unsafe to defer past merge and block merge. -->

### 2. [Category] Summary

**Location**: `filename:line`

**Problem**:
...

**Basis**:

- ...

**Completion condition**:

- ...

<!-- Findings from the Contract SubAgent. They diverge from the spec contract and block merge. -->

### 3. [Category] Summary

**Location**: `filename:line`

**Problem**:
...

**Basis**:

- ...

**Completion condition**:

- ...

---

Reviewed by <reviewer-name> at `<short-sha>`
