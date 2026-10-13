# test-prune

[日本語](README_ja.md)

Examines every test in the codebase and lists the ones that can be deleted or merged. The criterion is "if this test were deleted, what realistic bug would go unnoticed?"; neither test count nor coverage is a goal.

## Usage

- "テストを減らして"
- "不要なテストを洗い出して"
- "テストを整理して"

```text
/test-prune
```

## Behavior

- Reviews all tests in the codebase and lists every test that can be aggressively deleted or merged.
- Targets: copies of the implementation, mocks verifying themselves, re-checks of what types or libraries already guarantee, duplicates of other tests, over-reliance on internals, and excessive case splitting.
- A test is not kept "just in case". Its guarantee is weighed against run time, flakiness, and the cost of maintaining it.
- Preserving the test count or coverage is not a goal in itself.

The full procedure lives in [SKILL.md](SKILL.md).
