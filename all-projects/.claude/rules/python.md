---
paths: ["**/*.py", "**/pyproject.toml"]
---

# Python

## Toolchain

- Environments and packages via `uv` (`uv add`, `uv sync`, `uv run`) — not pip, poetry, or conda.
- Exception: Odoo projects manage dependencies via Docker/requirements.txt — skip the uv rule there; everything else below still applies.
- Format and lint with Ruff: `uv run ruff format .` then `uv run ruff check --fix .`.
- Hold new and changed code to the `mypy --strict` bar: full annotations on params, returns, and class attributes; no implicit `Any`.
- `# type: ignore[error-code]` only with the specific error code and a reason on the same line.
- Modern typing syntax: `list[str]`, `str | None` — not `List`, `Optional`, `Union`.

## Pydantic v2

- v2 idioms only: `model_validate`, `model_dump`, `model_config = ConfigDict(...)`, `@field_validator`, `@model_validator`.
- Never v1 idioms: `.dict()`, `.parse_obj()`, `class Config:`, `@validator`, `__fields__`.

## Async

- Never block the event loop: no `time.sleep`, `requests`, or sync DB drivers in async code — use `asyncio.sleep`, `httpx.AsyncClient`, asyncpg / SQLAlchemy async.
- One `AsyncSession` per task: never share a session across concurrent coroutines; use `async with session_factory() as session:`.
- No fire-and-forget tasks: keep references, await or gather them, and handle their exceptions explicitly.

## Tests

- pytest style: plain functions + fixtures; `@pytest.mark.parametrize` instead of loops; `pytest.raises(SpecificError)` for error paths.
- Meet the project's coverage gate (80-90%) with meaningful assertions — never pad with assertion-free tests.
- Done means the gate ran clean with output shown. Default gate when the project defines none: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`, `uv run pytest`.
