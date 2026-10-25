"""Entry: `reverseiii-scrape` → runs patch + meta scraper once."""
from __future__ import annotations

import argparse
import asyncio
import sys

from reverseiiiiing.meta.scraper import run_once
from reverseiiiiing.utils.config import load_config


def main() -> int:
    ap = argparse.ArgumentParser(prog="reverseiii-scrape")
    ap.add_argument("--config", default="config/config.yaml")
    args = ap.parse_args()
    cfg = load_config(args.config)
    asyncio.run(run_once(cfg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
