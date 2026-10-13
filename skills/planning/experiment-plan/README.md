# experiment-plan

[日本語](README_ja.md)

Interview the user about a machine learning experiment (training or evaluating a model) and save the result as an experiment plan to `.mjun/experiments/YYYYMMDD_<slug>.md`, copied from `templates/template_experiment_plan.md`. The plan fixes the purpose, a falsifiable hypothesis, and the judgment criteria before the experiment runs, so that results and discussion can be added afterwards.

For general plans or designs, use [`grill-me`](../grill-me/README.md) or [`grill-self`](../grill-self/README.md) instead. This skill is also not for marking a plan complete or filling in results.

## Usage

- "機械学習の実験計画を作って"
- "評価実験を計画書にして"

## Behavior

1. Gather what is already known from the conversation and the codebase.
2. Ask the open questions one at a time, in this order (items clear from context are skipped): purpose, hypothesis (with the numeric criteria for support or refutation), experiment design (models, data, settings, baselines, metrics, evaluation set), implementation (items needed and what existing assets cover), scope (out of scope, known risks, related plans and issues).
3. Get the user's approval of the decisions, keeping each answer tied to its question.
4. Save the plan to `.mjun/experiments/YYYYMMDD_<slug>.md` (creating the directory if needed, using the creation date, no sequence numbers). The `Status` in the meta table starts as `planning` or `in-progress`.
5. Format with `oxfmt .mjun/experiments/` (skipped if `oxfmt` is missing), then report the file path, purpose, and hypothesis. Commit only when the user asks.

Question rules: one question at a time, each with a recommended option and the reason, asked through a choice tool such as `AskUserQuestion`. Facts the codebase can answer are looked up, not asked. When the needed decisions are in place, the skill offers to end the interview and continues only if the user asks.

Plan-writing rules:

- Do not fill in results at the planning phase: sections from `## 実験結果` onward (hypothesis verification, discussion, outlook) stay as headings only.
- `## 実装` lists implementation items only. Detailed steps, commands, and code snippets belong in issues or PRs, linked from the meta table and the `## 実装` issue list.
- Make each hypothesis verifiable as "supported", "partially supported", "refuted", or "not verifiable", with the agreed numeric criteria and comparison target.
- When an identifier such as `H1`, `Phase 2`, or `Exp 1` is referenced from another section, file, the meta table, or the table of contents, add a readable name (for example "H1: 弱教師強化").
- Keep the table of contents in sync with the headings.

## Dependencies

- `oxfmt` (optional, for formatting)

The full procedure lives in [SKILL.md](SKILL.md).
