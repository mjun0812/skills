# planning

Skills for turning a vague plan into decided, written-down choices. Two of them work through a design tree one decision at a time; the third produces a machine learning experiment plan.

## Which skill to use

| Situation                                                                | Skill             |
| ------------------------------------------------------------------------ | ----------------- |
| Resolve every open decision by asking the user, one question at a time   | `grill-me`        |
| Resolve every open decision by research and self-questioning, no prompts | `grill-self`      |
| Write a machine learning experiment plan through an interview            | `experiment-plan` |

`grill-me` and `grill-self` follow the same tree-walking approach (depth before breadth, investigate the codebase before deciding) and differ only in who decides.

## grill-me

Interview the user about a plan or design until no decision point is left. Each question is asked alone, comes with a recommended answer and its reason, and is posed through a choice prompt such as `AskUserQuestion`. Facts that the codebase can answer are looked up instead of asked. When a topic is exhausted the skill offers to stop, and on finishing it presents the full question-and-answer history.

- Trigger phrases: "計画を詰めて", "計画を改善して", "設計を厳しく問い詰めて".

## grill-self

The same walk, but the agent answers its own questions. For each decision point it states the question, researches, proposes with reasons, raises one counter-argument, then adopts with a confidence of high, medium, or low. Value judgments that only the user can make are provisionally adopted at low confidence rather than blocking. The output is a decision log table (question, decision, reason, confidence) with low-confidence items listed again as "needs confirmation".

- Trigger phrases: "自分で判断して計画を詰めて", "質問せずに設計を詰めて", "grill-selfして".

## experiment-plan

Produce an experiment plan for training or evaluating a machine learning model and save it to `.mjun/experiments/YYYYMMDD_<slug>.md` from `experiment-plan/templates/template_experiment_plan.md`. The interview covers purpose, a falsifiable hypothesis with numeric criteria, design (models, data, baselines, metrics, evaluation set), implementation items, and scope, one question at a time with a recommendation each.

The plan is written before the experiment runs: result sections are left as empty headings, implementation is a list of items linked to issues rather than commands, and identifiers such as `H1` always carry a readable name when referenced elsewhere. The file is formatted with `oxfmt` and committed only when the user asks.

- Trigger phrases: "機械学習の実験計画を作って", "評価実験を計画書にして".
- Not for general plans, marking a plan complete, or filling in results.

The question template and plan-writing rules live in each skill's `SKILL.md`.
