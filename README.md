# 词源奇旅 / English Word Stories

一个基于 **DeepAgents（Python）** 的英文单词深度解析 Agent App。

## 功能

- **单词深度解析**：按 `english-word` skill 生成词源、核心语义、历史源流、活的用法与金句。
- **结果保存**：每次新生成的结果都会归档为 Markdown 文档，包含输出内容、metadata、创建时间等信息。
- **结果缓存**：重复查询同一个英文单词时，优先返回该单词最新归档结果。
- **Claude 风格 Web UI**：包含单词查询栏、使用模型、生成时间、最近归档记录。
- **更易配的模型 UI**：支持 Provider 下拉、模型名称输入，并实时提示应配置的 `.env` 变量名。

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

### 新增 Provider

当前实现已改为**通用 provider 前缀解析**：

- `provider:model_name` 中的 `provider`
- 会自动映射到：
  - `{PROVIDER}_API_KEY`
  - `{PROVIDER}_BASE_URL`
- 若未提供，则回退到：
  - `LLM_API_KEY`
  - `LLM_BASE_URL`

其中 provider 环境变量前缀会自动规范化为大写下划线，例如：

- `openai` → `OPENAI_API_KEY`
- `anthropic` → `ANTHROPIC_API_KEY`
- `google-genai` → `GOOGLE_GENAI_API_KEY`
- `google_genai` → `GOOGLE_GENAI_API_KEY`

示例：

```env
DEEPAGENT_DEFAULT_MODEL=groq:llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_key
```

```env
DEEPAGENT_DEFAULT_MODEL=google-genai:gemini-2.5-pro
GOOGLE_GENAI_API_KEY=your_google_key
```

注意：

- 是否需要安装额外依赖，取决于该 provider 是否有对应的 LangChain 集成包。
- 模型名请以 provider 官方文档/控制台为准。
