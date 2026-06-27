from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from app.config import APP_NAME_EN, APP_NAME_ZH, ARCHIVE_ROOT

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


@dataclass(slots=True)
class ArchiveRecord:
    metadata: dict[str, Any]
    body: str
    output_markdown: str
    path: Path


def normalize_word(raw_word: str) -> tuple[str, str]:
    cleaned = re.sub(r"\s+", " ", raw_word.strip())
    if not cleaned:
        raise ValueError("请输入英文单词。")
    if " " in cleaned:
        raise ValueError("目前只支持查询单个英文单词。")
    if not re.fullmatch(r"[A-Za-z][A-Za-z'\-]*", cleaned):
        raise ValueError("请输入合法的英文单词，只支持字母、连字符和单引号。")

    normalized = cleaned.lower()
    display_word = normalized[:1].upper() + normalized[1:]
    return normalized, display_word


def archive_dir_for(word: str) -> Path:
    return ARCHIVE_ROOT / word


def build_archive_markdown(metadata: dict[str, Any], output_markdown: str) -> str:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    body = f"""# {APP_NAME_ZH} / {APP_NAME_EN} Archive

## Metadata

- **Word**: {metadata["display_word"]}
- **Model**: {metadata["model"]}
- **Created At**: {metadata["created_at"]}
- **Duration (ms)**: {metadata["duration_ms"]}
- **Cache Key**: {metadata["cache_key"]}
- **Skill**: {metadata["skill"]}

## Output

{output_markdown.strip()}
"""
    return f"---\n{frontmatter}\n---\n\n{body.strip()}\n"


def save_archive(
    *,
    word: str,
    display_word: str,
    model: str,
    output_markdown: str,
    duration_ms: int,
) -> ArchiveRecord:
    now = datetime.now().astimezone()
    archive_dir = archive_dir_for(word)
    archive_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{now.strftime('%Y%m%d-%H%M%S')}--{word}.md"
    path = archive_dir / filename

    metadata = {
        "app_name_zh": APP_NAME_ZH,
        "app_name_en": APP_NAME_EN,
        "skill": "english-word",
        "word": word,
        "display_word": display_word,
        "cache_key": word,
        "model": model,
        "created_at": now.isoformat(),
        "duration_ms": duration_ms,
        "archive_filename": filename,
    }

    markdown_text = build_archive_markdown(metadata, output_markdown)
    path.write_text(markdown_text, encoding="utf-8")
    return ArchiveRecord(metadata=metadata, body=markdown_text, output_markdown=output_markdown.strip(), path=path)


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content
    metadata = yaml.safe_load(match.group(1)) or {}
    body = content[match.end() :].lstrip()
    return metadata, body


def _extract_output_markdown(body: str) -> str:
    marker = "\n## Output\n"
    if marker in body:
        return body.split(marker, 1)[1].strip()
    return body.strip()


def load_archive(path: Path) -> ArchiveRecord:
    content = path.read_text(encoding="utf-8")
    metadata, body = _split_frontmatter(content)
    output_markdown = _extract_output_markdown(body)
    return ArchiveRecord(metadata=metadata, body=body, output_markdown=output_markdown, path=path)


def find_latest_archive(word: str) -> ArchiveRecord | None:
    directory = archive_dir_for(word)
    if not directory.exists():
        return None
    candidates = sorted(directory.glob("*.md"), reverse=True)
    if not candidates:
        return None
    return load_archive(candidates[0])


def list_recent_archives(limit: int = 12) -> list[ArchiveRecord]:
    records: list[ArchiveRecord] = []
    for file_path in sorted(ARCHIVE_ROOT.glob("*/*.md"), reverse=True):
        try:
            records.append(load_archive(file_path))
        except Exception:
            continue
        if len(records) >= limit:
            break
    return records
