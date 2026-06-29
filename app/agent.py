from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from app.config import DEFAULT_MODEL, PROJECT_ROOT

SYSTEM_PROMPT = """
你是“词源奇旅 / English Word Stories”的专用单词解析 Agent。

必须始终遵守 english-word skill 的结构与文风要求。
任务目标不是翻译，而是帮助用户从词源、语义骨架、历史演变与真实用法中吃透一个英文单词。

硬性要求：
1. 每次只解析一个英文单词。
2. 输出必须是最终 Markdown，不要额外前言、不要解释你将做什么、不要使用代码块包裹整体内容。
3. 尽量直接给出完整答案，不要调用无关工具。
4. 优先保证结构完整、语言有洞见、叙事自然。
""".strip()


def build_user_prompt(word: str) -> str:
    return (
        f'Deeply explain the word "{word}". '
        "Use the english-word skill exactly and return only the final Markdown answer."
    )


def _split_model(model: str) -> tuple[str, str]:
    if ":" in model:
        provider, model_name = model.split(":", 1)
        return provider.strip().lower(), model_name.strip()
    return "", model.strip()


def _normalize_provider_env_prefix(provider: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", provider.strip().upper()).strip("_")


def _provider_env_keys(provider: str, name: str) -> list[str]:
    keys: list[str] = []
    normalized_prefix = _normalize_provider_env_prefix(provider)
    if normalized_prefix:
        keys.append(f"{normalized_prefix}_{name}")
    keys.append(f"LLM_{name}")
    return keys


def _resolve_env(provider: str, name: str) -> str | None:
    for key in _provider_env_keys(provider, name):
        value = os.getenv(key)
        if value:
            return value
    return None


def _validate_model(model: str) -> tuple[str, str]:
    provider, model_name = _split_model(model)
    if not model_name:
        raise RuntimeError("模型名称不能为空。请使用 `provider:model_name` 或直接填写模型名。")
    return provider, model_name


def build_model(model: str):
    provider, model_name = _validate_model(model)
    api_key = _resolve_env(provider, "API_KEY")
    base_url = _resolve_env(provider, "BASE_URL")

    if provider == "openai":
        return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
    if provider == "anthropic":
        return ChatAnthropic(model_name=model_name, api_key=api_key, base_url=base_url)
    if provider:
        kwargs: dict[str, Any] = {}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        return init_chat_model(model_name, model_provider=provider, **kwargs)
    return model


@lru_cache(maxsize=8)
def get_agent(model: str = DEFAULT_MODEL):
    backend = FilesystemBackend(root_dir=PROJECT_ROOT, virtual_mode=True)
    return create_deep_agent(
        model=build_model(model),
        system_prompt=SYSTEM_PROMPT,
        backend=backend,
        skills=["/skills"],
        name="english-word-stories",
    )


def _coerce_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part and part.strip()).strip()
    return str(content).strip()


def extract_markdown(result: Any) -> str:
    if isinstance(result, dict):
        structured = result.get("structured_response")
        if isinstance(structured, str) and structured.strip():
            return structured.strip()

        messages = result.get("messages")
        if isinstance(messages, list):
            for message in reversed(messages):
                if isinstance(message, AIMessage):
                    text = _coerce_content(message.content)
                    if text:
                        return text
                elif isinstance(message, BaseMessage):
                    text = _coerce_content(message.content)
                    if text:
                        return text
                elif isinstance(message, dict) and message.get("role") == "assistant":
                    text = _coerce_content(message.get("content"))
                    if text:
                        return text

        output = result.get("output")
        if isinstance(output, str) and output.strip():
            return output.strip()

    text = _coerce_content(result)
    if text:
        return text
    raise RuntimeError("DeepAgent 未返回可解析的文本结果。")


def generate_word_story(word: str, model: str | None = None) -> str:
    selected_model = (model or DEFAULT_MODEL).strip()
    agent = get_agent(selected_model)
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": build_user_prompt(word),
                }
            ]
        }
    )
    return extract_markdown(result)
