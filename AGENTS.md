# AGENTS.md — Review Contract

GGA (Gentle Guardian Angel) uses this file as the review rules for every PR and
commit. It is the single source of truth for what "done" means in this repo.

## Commit Conventions

- Use Conventional Commits: `type(scope): subject`.
- Allowed scopes: `api`, `ui`, `db`, `models`, `data`, `conf`.
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `revert`.
- Subject: imperative mood, lowercase, no trailing period, max 50 characters.

## Mandatory Gates (before every commit)

All gates must pass before committing. Run them via the Makefile:

- `make lint` — ruff check: E, F, I, UP, B, S via `.code_quality/ruff.toml`.
- `make check` — ruff format check, line-length 100.
- `make types` — mypy via `.code_quality/mypy.ini`.
- `make test` — pytest `backend/tests/`.

## FastAPI / Backend Patterns

- Use FastAPI lifespan for startup/shutdown (model loading, resources); logging config at import is acceptable.
- Inject dependencies with `Depends()`; never instantiate services in routes.
- Validate request/response payloads with Pydantic schemas.
- Use structured JSON logging; never plain `print()`.
- Services must not make HTTP calls; I/O lives in infrastructure adapters.
- Identifiers and paths in English; comments in Spanish.
- No `# noqa` abuse — fix the underlying issue.

## Python Hygiene

- Type hints on all new function signatures and public attributes; annotate existing signatures when you modify them. Pre-existing unannotated code is not a violation (mypy runs with `disallow_untyped_defs = False`); it is migrated incrementally.
- Never use bare `except:` — catch specific exceptions.
- Never use `print()` in application code; use `logging`.
- Keep functions small and single-purpose.
