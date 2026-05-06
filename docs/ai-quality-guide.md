# AI Quality Guide

This project uses AI to reduce the effort of starting, not to judge productivity.
The core product flow stays the same:

```text
Brain Dump -> several Suggestions -> Feedback -> Action
```

## Goal

- Turn unstructured Brain Dumps into several small action candidates.
- Help the user choose one starting point.
- Do not evaluate the user.
- Do not force priority.
- Do not use pressure language about failure, achievement rate, productivity score, or laziness.
- Optimize for starting, not completing.

## Good Suggestions

Good AI suggestions should:

- Be startable within 2-5 minutes.
- Contain one action per candidate.
- Use a short, clear `title`.
- Use a concrete `micro_step`.
- Avoid requiring too much setup.
- Prefer starting language over finishing language.
- Give the user multiple low-pressure choices.

Examples:

- `발표 자료 파일만 열기`
- `메일 첫 줄만 쓰기`
- `책상 위 물건 3개만 고르기`

## Poor Suggestions

Avoid suggestions that:

- Are too large, such as `프로젝트 완성하기`.
- Use pressure language, such as `무조건 해야 함`.
- Bundle several actions in one sentence.
- Stay abstract.
- Evaluate the user.
- Mention failure, laziness, achievement rate, or productivity score.

## make_smaller Quality

`make_smaller` must return a smaller action than the original suggestion.

Rules:

- Return 1-3 candidates.
- Do not repeat the original action with the same wording.
- Keep only one action.
- Reduce to a 30-second to 2-minute starting move when possible.
- Prefer actions like opening a file, writing only the title, writing only the first line,
  choosing only three items, clicking one button, or moving one object.

## Cost Policy

- Default CI and `pytest` must not call OpenAI.
- Real OpenAI smoke tests are opt-in only with `RUN_REAL_AI_SMOKE=true`.
- Prompt changes should be validated first with fixtures, schema checks, and quality validators.
- After changing prompts, run real AI calls only on a minimal sample set.
- Prompt version changes should update `AI_PROMPT_VERSION` so cache keys and usage logs remain clear.

## Current v2 Focus

Prompt v2 improves:

- Smaller first actions.
- Avoidance of pressure language.
- Better `make_smaller` behavior.
- Clearer single-action suggestions.

AI quality tuning that uses repeated real calls is intentionally deferred because it can incur API cost.
