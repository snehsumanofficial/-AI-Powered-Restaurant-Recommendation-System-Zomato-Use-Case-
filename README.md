# AI-Powered Restaurant Recommendation System

This repository contains the phase-wise implementation for the restaurant recommendation architecture.

## Current coverage

- Phase 1: Foundation and project skeleton
- Phase 2: Data ingestion and preprocessing
- Phase 3: Groq LLM connection baseline

## Project structure

```text
src/
  phases/
    phase1/    # foundation, settings, app entry
    phase2/    # ingestion, schema mapping, cleaning, repository
    phase3/    # Groq LLM client baseline
  app/         # compatibility wrapper entrypoints
  config/      # compatibility wrapper config
  data/        # compatibility wrapper data modules
tests/
  fixtures/    # offline fixtures for deterministic tests
```

## Environment variables

Set these in a `.env` file or shell environment:

- `LLM_API_KEY` or `GROQ_API_KEY` (required for Groq tests/phase 3)
- `LLM_MODEL` (default: `llama-3.3-70b-versatile`)
- `DATA_CACHE_DIR` (default: `.cache/huggingface`)
- `DATASET_NAME` (default: `ManikaSaini/zomato-restaurant-recommendation`)
- `DATASET_SPLIT` (default: `train`)
- `DATASET_REVISION` (optional pinned revision/commit)
- `SAMPLE_LIMIT` (optional integer, limits records for quick runs)
- `DATA_FIXTURE_PATH` (optional local JSON fixture path for offline/dev runs)
- `LOG_LEVEL` (default: `INFO`)
- `RUN_GROQ_LIVE` (`1` to run live Groq connectivity test, default: `1`)

## Run

```bash
python -m src.app
```

### Backend + Frontend (end-to-end)

Run backend:

```bash
py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000
```

Run frontend in another terminal:

```bash
py -m http.server 5173 --directory frontend
```

Open: `http://127.0.0.1:5173`

## Test

```bash
python -m pytest
```
