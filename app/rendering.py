from __future__ import annotations

from markdown import markdown


def render_markdown_to_html(markdown_text: str) -> str:
    return markdown(
        markdown_text,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
