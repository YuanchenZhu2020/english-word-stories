---
name: english-word
description: Deep-dive English word mastery tool. Deconstructs a single English word into core semantics and epiphany. Use when user asks to explain/master a specific English word.
user-invocable: true
metadata:
    version: "1.2.0"
---

## Usage

<example>
User: Deeply explain the word "Serendipity".
User: 深度解析 "incubate" 这个词
User: 帮我吃透 "ubiquitous"
Assistant: [Calls english-word with the given word]
</example>

## Instructions

目标不是翻译，而是让用户**从骨子里掌握**这个词看见它的源头，理解它的骨架，最终能用它思考。

针对输入的 `word`（输出时首字母大写，其余小写），进行以下分析，直接在对话中用 Markdown 输出：

### 输出结构

#### 1. 标题行

```
## {Word}  /{音标}/  {中文翻译}
```

#### 2. 核心语义

```markdown
- **原始画面**: [用一句话描述该词词源中最具画面感的物理场景。例如 Incubate  母鸡伏在蛋上，用体温等待生命破壳。]
- **核心意象**: [提炼为一个公式，用 `+` 和 `=` 连接关键词素。例如 温暖 + 时间 + 保护 = 孕育]
- **深层解释**: [23 段，完成以下递进：]
    1. **结构拆解**: [前缀/词根/后缀各贡献了什么含义？（形态分解，不涉及历史演变）]
    2. **语义辐射**: [这个词如何从核心意象延伸到不同领域？各领域义项之间的内在逻辑是什么？]
    3. **使用直觉**: [什么场景下母语者会*本能地*选择这个词而非近义词？它携带什么情感色彩和语域？]
```

写作要求：用充满洞见的语言阐述，分段清晰，**加粗**关键词，有穿透力，避免教科书式的平铺直叙。

#### 3. 历史源流

以时间为线索，讲述这个词的"生平故事"：

- **诞生**: 最早出现在什么时代、何种语言？最初的形式和本义是什么？
- **演变**: 经历了哪些关键的语义转折？每次转变背后的社会、文化或认知动因是什么？
- **今生**: 现代英语中的核心义项是如何沉淀形成的？

写作要求：用**叙事**而非罗列的方式，让词的历史像一条流动的河，从源头淌到今天。控制在 24 句，精炼有力，不要写成学术论文。

#### 4. 活的用法

给出 1-2 个**典型搭配或句型**，每个配一个短句示例，展示该词在真实语境中的使用方式。

```
- **{搭配/句型}**  {短句示例}
```

#### 5. 一语道破

一句中英双语的金句，必须具有哲学高度，总结该词的灵魂。用引用格式：

```
> "English sentence. 中文金句。"
```
