# 词源奇旅 / English Word Stories

一个基于 **DeepAgents（Python）** 的英文单词深度解析 Agent App。

## 功能

- **单词深度解析**：按 `english-word` skill 生成词源、核心语义、历史源流、活的用法与金句。
- **结果保存**：每次新生成的结果都会归档为 Markdown 文档，包含输出内容、metadata、创建时间等信息。
- **结果缓存**：重复查询同一个英文单词时，优先返回该单词最新归档结果。
- **Claude 风格 Web UI**：包含单词查询栏、使用模型、生成时间、最近归档记录。

## 环境要求

- Python 3.12+
- `uv`
- 至少配置一个可用模型的 API Key，例如：
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - 也支持在 `.env` 中配置自定义 API 端点（Base URL）

## 启动

```powershell
uv venv .venv
uv pip install --python .\.venv\Scripts\python.exe -e .
Copy-Item .env.example .env
# 编辑 .env 填入你的 API Key / Base URL

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

打开浏览器访问：

```text
http://127.0.0.1:8000
```

## 目录结构

```text
app/                 后端代码
archives/            归档结果
skills/english-word/ Skill 定义
static/              Web UI
```

## `.env` 配置说明

应用支持两类环境变量：

### 1) 通用变量

当你希望不同 provider 共用同一套网关配置时，可以使用：

```env
LLM_API_KEY=your_key
LLM_BASE_URL=https://your-llm-endpoint.example.com/v1
```

### 2) Provider 专属变量

当你希望不同 provider 使用不同配置时，可以使用：

```env
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
```

优先级：

- provider 专属变量优先
- 若未设置，则回退到通用变量 `LLM_API_KEY` / `LLM_BASE_URL`

例如：

- `DEEPAGENT_DEFAULT_MODEL=anthropic:claude-sonnet-4-6` 时，优先读取 `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL`
- `DEEPAGENT_DEFAULT_MODEL=openai:gpt-5` 时，优先读取 `OPENAI_API_KEY` / `OPENAI_BASE_URL`
