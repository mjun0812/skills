# review

## test-prune

Examine every test in the codebase and list the ones that can be deleted or merged. Targets are copies of the implementation, mocks verifying themselves, re-checks of what types or libraries already guarantee, duplicates of other tests, over-reliance on internals, and excessive case splitting. The criterion is "if this test were deleted, what realistic bug would go unnoticed?"; neither test count nor coverage is a goal.

- Trigger phrases: "テストを減らして", "不要なテストを洗い出して", "テストを整理して".
