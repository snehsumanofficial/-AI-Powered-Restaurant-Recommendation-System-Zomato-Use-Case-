from __future__ import annotations

import logging

from src.phases.phase1.settings import load_settings
from src.phases.phase2.loader import load_restaurants


def main() -> None:
    settings = load_settings()
    logger = logging.getLogger("app")
    logger.info("startup")
    repo = load_restaurants(settings)
    logger.info("restaurants_loaded count=%s", len(repo.get_all()))
    print(f"Loaded {len(repo.get_all())} restaurants")


if __name__ == "__main__":
    main()
