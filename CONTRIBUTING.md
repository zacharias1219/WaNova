# Contributing to WaNova

Thanks for helping improve this project. This repo is a WhatsApp-first AI agent built with **FastAPI**, **LangGraph**, and the **Meta WhatsApp Cloud API**.

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Before you start

- **Python** 3.12+ (see `pyproject.toml`)
- **[uv](https://docs.astral.sh/uv/)** for installs and running commands
- **Docker** / Docker Compose for the full stack (`docker compose`)
- A filled **`.env`** from `.env.example` when running integration paths (webhook, external APIs)

## Quick dev setup

```bash
git clone https://github.com/zacharias1219/whatsapp-agent.git
cd whatsapp-agent
cp .env.example .env
# Edit .env with your keys where needed
uv sync
```

Optional: install pre-commit hooks (same checks as CI-style local workflow):

```bash
uv run pre-commit install
```

## Running tests

From the repo root:

```bash
uv run pytest
```

Useful variants:

```bash
uv run pytest -q
uv run pytest tests/test_whatsapp_webhook.py -v
```

## Linting and formatting

This project uses **Ruff** (see `Makefile` for the full recipe list).

```bash
uv run ruff format .
uv run ruff check --select I --fix .
uv run ruff check --fix .
```

Check-only (no writes):

```bash
uv run ruff format --check .
uv run ruff check .
```

## What makes a good PR

1. **Scope** — One logical change per PR (bugfix, feature, docs, tests).
2. **Tests** — Add or update tests when behavior changes; keep existing tests green.
3. **Secrets** — Never commit API keys, tokens, or real phone numbers; use env vars and placeholders in docs.
4. **Docs** — If you change setup or behavior, update `README.md` or `docs/` as needed.

## Reporting issues

- Use [GitHub Issues](https://github.com/zacharias1219/whatsapp-agent/issues).
- Include: what you expected, what happened, Python/OS version, and minimal steps to reproduce.
- For **security-sensitive** reports, do **not** open a public issue — see [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under the same license as the project ([MIT](LICENSE)).
