from __future__ import annotations

import time

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent import generate_word_story
from app.archive import find_latest_archive, list_recent_archives, normalize_word, save_archive
from app.config import APP_NAME_EN, APP_NAME_ZH, DEFAULT_MODEL, PROJECT_ROOT, STATIC_ROOT
from app.rendering import render_markdown_to_html
from app.schemas import AppConfigResponse, ArchiveSummary, QueryRequest, QueryResponse

app = FastAPI(title=f"{APP_NAME_ZH} / {APP_NAME_EN}")
app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")


def _to_summary(record) -> ArchiveSummary:
    metadata = record.metadata
    return ArchiveSummary(
        word=metadata.get("word", ""),
        display_word=metadata.get("display_word", metadata.get("word", "")),
        model=metadata.get("model", ""),
        created_at=metadata.get("created_at", ""),
        filename=record.path.name,
        path=str(record.path.relative_to(PROJECT_ROOT)),
    )


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_ROOT / "index.html")


@app.get("/api/config", response_model=AppConfigResponse)
def get_config() -> AppConfigResponse:
    recent = [_to_summary(record) for record in list_recent_archives()]
    return AppConfigResponse(
        app_name_zh=APP_NAME_ZH,
        app_name_en=APP_NAME_EN,
        default_model=DEFAULT_MODEL,
        recent_archives=recent,
    )


@app.get("/api/archives", response_model=list[ArchiveSummary])
def archives() -> list[ArchiveSummary]:
    return [_to_summary(record) for record in list_recent_archives(limit=24)]


@app.post("/api/query", response_model=QueryResponse)
def query_word(payload: QueryRequest) -> QueryResponse:
    try:
        word, display_word = normalize_word(payload.word)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    model = (payload.model or DEFAULT_MODEL).strip()

    if not payload.force_refresh:
        cached = find_latest_archive(word)
        if cached is not None:
            return QueryResponse(
                word=word,
                display_word=display_word,
                model=cached.metadata.get("model", model),
                created_at=cached.metadata.get("created_at", ""),
                from_cache=True,
                duration_ms=0,
                archive_path=str(cached.path.relative_to(PROJECT_ROOT)),
                markdown_output=cached.output_markdown,
                html_output=render_markdown_to_html(cached.output_markdown),
                metadata=cached.metadata,
            )

    started = time.perf_counter()
    try:
        markdown_output = generate_word_story(display_word, model=model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    duration_ms = int((time.perf_counter() - started) * 1000)

    saved = save_archive(
        word=word,
        display_word=display_word,
        model=model,
        output_markdown=markdown_output,
        duration_ms=duration_ms,
    )
    return QueryResponse(
        word=word,
        display_word=display_word,
        model=model,
        created_at=saved.metadata["created_at"],
        from_cache=False,
        duration_ms=duration_ms,
        archive_path=str(saved.path.relative_to(PROJECT_ROOT)),
        markdown_output=saved.output_markdown,
        html_output=render_markdown_to_html(saved.output_markdown),
        metadata=saved.metadata,
    )


def run() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
