<!--
Every PR must link an approved issue. Replace NNN with the real issue number and
keep the keyword (Closes/Fixes/Resolves). The issue must carry `status:approved`.
-->

Closes #NNN

## Type

Check exactly ONE box, then add the matching `type:*` label to the PR.

- [ ] Bug fix — `type:bug`
- [ ] New feature — `type:feature`
- [ ] Documentation only — `type:docs`
- [ ] Code refactoring — `type:refactor`
- [ ] Maintenance/tooling — `type:chore`
- [ ] Breaking change — `type:breaking-change`

## Summary

-

## Changes

| File | Change |
|------|--------|
| `` |  |

## Test plan

- [ ] Lint: `uvx ruff check --config .code_quality/ruff.toml backend frontend`
- [ ] Format: `uvx ruff format --check --config .code_quality/ruff.toml backend frontend`
- [ ] Backend suite: `pytest backend/tests -q`
- [ ] Frontend suite: `pytest frontend/tests -q`
- [ ] Images build: `docker compose build`
- [ ] Manually exercised the affected flow

## Checklist

- [ ] Linked an issue that carries `status:approved`
- [ ] Added exactly one `type:*` label
- [ ] Conventional commit messages
- [ ] No `Co-Authored-By` trailers
- [ ] Docs updated if behavior changed
