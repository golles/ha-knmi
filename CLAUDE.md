# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

KNMI is a custom component (integration) for Home Assistant that exposes Dutch weather
data from KNMI via the [weerlive.nl](https://weerlive.nl) API. The integration is
distributed through HACS. All API calls are delegated to the external `weerlive-api`
Python package (`weerlive` module); this repo contains only the Home Assistant glue.

The component lives in `custom_components/knmi/`. The `config/` directory holds a runnable
Home Assistant configuration for local development, and `tests/` mirrors the component
modules.

## Commands

The project uses [uv](https://docs.astral.sh/uv) for Python dependency management and `npm`
only for Prettier.

- Setup environment: `./scripts/setup_env.sh` (installs uv + npm deps, pre-commit hooks)
- Run all tests: `uv run pytest` (coverage is on by default via `pyproject.toml` addopts)
- Run a single test file: `uv run pytest tests/test_sensor.py`
- Run a single test: `uv run pytest tests/test_sensor.py::test_name`
- Run all CI lint/type checks locally: `./scripts/local_ci_checks.sh` (parses and runs the
  check matrix from `.github/workflows/ci.yaml`)
- Run a live Home Assistant with this integration: `./scripts/develop.sh` (serves the
  `config/` dir; installs the `runhass` dependency group)
- Type check: `uv run mypy .`
- Lint/format: `uv run ruff check .` and `uv run ruff format --check .`

Individual CI checks (matching the CI matrix): `mypy`, `pylint custom_components/knmi tests`,
`ruff check`, `ruff format --check`, `shellcheck scripts/*.sh`, `uv lock --check`, `yamllint`,
and Prettier (`npm run prettier -- --check .`).

## Architecture

Standard Home Assistant config-entry + coordinator pattern. Data flows in one direction:
the coordinator fetches a `weerlive.Response` object, and every entity reads from it via
lambdas in its `EntityDescription`.

- **`__init__.py`** — `async_setup_entry` builds a `WeerliveApi` client and a
  `KnmiDataUpdateCoordinator`, stores the coordinator on `config_entry.runtime_data`, and
  forwards setup to the platforms in `PLATFORMS` (binary_sensor, sensor, weather).
  Also contains `async_migrate_entry` (config entry version migrations; currently v1→v2
  wipes old entities).
- **`coordinator.py`** — `KnmiDataUpdateCoordinator` extends `DataUpdateCoordinator[Response]`.
  `_async_update_data` calls `client.latitude_longitude(...)` using the lat/lon stored on the
  config entry and raises `UpdateFailed` on any error.
- **`entity.py`** — `KnmiEntity` (base `CoordinatorEntity`) and `KnmiEntityDescription`, a
  frozen dataclass extending `EntityDescription` with a `state_attributes_fn(Response) -> dict`.
  All platforms subclass these.
- **Platform modules** (`sensor.py`, `binary_sensor.py`, `weather.py`) — each defines a
  `DESCRIPTIONS` list of frozen dataclasses combining `KnmiEntityDescription` with the
  HA platform's description class. Each description carries `value_fn` (and sometimes
  `state_attributes_fn`) lambdas that extract values from the `Response` object. Adding a
  sensor means adding a `*Description` entry plus its `translation_key` strings — not a new class.
- **`config_flow.py`** — UI config flow (name, latitude, longitude, API key) plus an options
  flow for scan interval. Validates the API key against `weerlive` during setup. `VERSION = 2`.
- **`const.py`** — minimal: `DOMAIN`, `NAME`, defaults. Keep in sync with `manifest.json`
  (enforced by `tests/test_metadata.py`).

## Conventions

- Ruff is configured with `select = ["ALL"]` and a 150-char line length; Google docstring
  convention. New code must pass the full ruff ruleset.
- Translations live in `custom_components/knmi/translations/` (`en.json`, `nl.json`). Entity
  names come from `translation_key` on each description — both files must define the key.
  API _data_ (weather descriptions, etc.) is Dutch-only.
- Tests use `pytest-homeassistant-custom-component`. `tests/conftest.py` auto-patches
  `WeerliveApi` everywhere and provides a `mocked_data` fixture that loads a JSON fixture from
  `tests/fixtures/` into a `Response`; parametrize it via `@pytest.mark.parametrize(..., indirect=True)`.
  All entities are force-enabled in tests via the `enable_all_entities` fixture.
- `tests/test_metadata.py` enforces that `const.py`/`manifest.json` agree and that the
  `weerlive-api` version matches between `pyproject.toml` and `manifest.json`. When bumping the
  dependency, update both files.
- Requires Python 3.14 and `homeassistant>=2026.0.0`.
