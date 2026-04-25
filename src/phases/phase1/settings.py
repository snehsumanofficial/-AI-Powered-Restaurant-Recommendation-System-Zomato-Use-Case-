from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    llm_api_key: str | None
    llm_model: str
    data_cache_dir: Path
    dataset_name: str
    dataset_split: str
    dataset_revision: str | None
    sample_limit: int | None
    data_fixture_path: Path | None
    log_level: str


def _load_dotenv_if_present() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(value)


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s event=%(message)s",
    )


def load_settings() -> Settings:
    _load_dotenv_if_present()
    settings = Settings(
        llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY"),
        llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        data_cache_dir=Path(os.getenv("DATA_CACHE_DIR", ".cache/huggingface")),
        dataset_name=os.getenv(
            "DATASET_NAME", "ManikaSaini/zomato-restaurant-recommendation"
        ),
        dataset_split=os.getenv("DATASET_SPLIT", "train"),
        dataset_revision=os.getenv("DATASET_REVISION"),
        sample_limit=_parse_optional_int(os.getenv("SAMPLE_LIMIT")),
        data_fixture_path=Path(os.getenv("DATA_FIXTURE_PATH"))
        if os.getenv("DATA_FIXTURE_PATH")
        else None,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    settings.data_cache_dir.mkdir(parents=True, exist_ok=True)
    _configure_logging(settings.log_level)
    return settings
