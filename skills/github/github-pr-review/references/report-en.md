# <reviewer-name> PR Review

<!--
Authoring rules:
- Summary describes only what the PR changes, in 1-2 sentences. Do not summarize the review result or finding counts.
- If CI has failing checks, or the Contract axis was skipped, add one line for each to the Summary.
- Findings only contains findings from the Finder, Standards, and Contract SubAgent that the verifier judged confirmed.
- Write in plain, natural language that a reader understands in one pass, explaining only the technical concepts that are needed in general terms. Do not add speculation, fix proposals, or implementation methods, and do not output the verification process.
- Findings from the Standards and Contract SubAgent also block merge and affect the Verdict.
- If Findings has no items, keep the heading and write "N/A".
- Separate findings with a `### N. [Category] Summary` heading each. List Finder findings first, Standards findings second, and Contract findings third, numbering all Findings sequentially from 1.
- Category is one to three words naming the main harm. Do not use processing state, overly broad viewpoints, causes or mechanisms, severity, or confidence.
- Summary states only the harm in one sentence; the cause belongs in `Problem`.
- Bold each field name on its own line and start its content on the next line. Separate fields with a blank line.
- Each Finder finding must include `Location` / `Problem` / `Execution path` / `Completion condition`.
- Each Standards or Contract finding must include `Location` / `Problem` / `Basis` / `Completion condition`.
- Add `Other locations` and `Notes` before `Completion condition` only when they apply.
- A Finder finding's `Problem` states only the triggering condition, cause, and concrete harm, in that order, in one paragraph of at most three sentences; keep the necessary premises and code names, and drop the verification process, evidence listings, and repetition.
- A Standards finding's `Problem` combines the facts visible in the diff and why deferring it until after merge is unsafe, in that order, without adding harms the facts do not show.
- A Contract finding's `Problem` combines the current state of the implementation and how it diverges from the contract's promise, in that order.
- `Execution path` is built from the Finder's `Evidence`: a numbered list of at most three hops starting at `path:line` and ending where the harm appears, one `file:line` (note) hop per line.
- `Basis` is a bullet list. For a Standards finding, cite the convention document's `file:line` and statement for a convention violation, or the code's `file:line` for a code smell, replacing smell names, principle names, and design jargon with observable facts. For a Contract finding, quote the relevant spec statement and cite the implementation `file:line`.
- `Other locations` is a bullet list of other `file:line` that share the same problem, one per line, and they do not stay in `Problem`.
- `Notes` is a bullet list of facts that are not the core problem but help judgment, such as comparisons with the pre-change behavior or the precedent, and they do not stay in `Problem`.
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
