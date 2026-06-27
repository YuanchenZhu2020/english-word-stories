from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_NAME_ZH = "词源奇旅"
APP_NAME_EN = "English Word Stories"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = PROJECT_ROOT / "archives"
STATIC_ROOT = PROJECT_ROOT / "static"
SKILLS_ROOT = PROJECT_ROOT / "skills"

DEFAULT_MODEL = os.getenv("DEEPAGENT_DEFAULT_MODEL", "anthropic:claude-sonnet-4-6")

ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
