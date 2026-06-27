from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    word: str = Field(min_length=1, max_length=64)
    model: str | None = Field(default=None, max_length=128)
    force_refresh: bool = False


class ArchiveSummary(BaseModel):
    word: str
    display_word: str
    model: str
    created_at: str
    filename: str
    path: str


class QueryResponse(BaseModel):
    word: str
    display_word: str
    model: str
    created_at: str
    from_cache: bool
    duration_ms: int
    archive_path: str
    markdown_output: str
    html_output: str
    metadata: dict[str, Any]


class AppConfigResponse(BaseModel):
    app_name_zh: str
    app_name_en: str
    default_model: str
    recent_archives: list[ArchiveSummary]
