---
name: semantic-understanding
description: 语义理解模块 — Ollama本地LLM驱动，解析新闻/舆情/财报/Serenity推文，输出结构化投资研究数据
tags: [semantic, nlp, ollama, news, sentiment, earnings, serenity]
last_updated: 2026-05-23
requires: ollama (llama3.2:3b), requests, Python3
---

# 语义理解模块 v1.0

Ollama本地LLM驱动，四大解析能力：新闻、舆情、财报、Serenity推文。

## 架构

```
输入文本 → Ollama(qwen2.5:1.5b或llama3.2:3b) → 结构化JSON → 存档/进一步处理
```

## 依赖

```bash
# 启动Ollama（后台运行）
terminal: /usr/local/bin/ollama serve
# 或：背景进程 session_id=proc_33434e6540f3 (ollama serve)

# 拉取模型（如需要）
ollama pull llama3.2:3b
# 或轻量版：
ollama pull qwen2.5:1.5b-instruct

# 验证
curl -s http://127.0.0.1:11434/api/tags
```

## 四大解析器

### 1. 新闻解析 (`parse_news`)
```python
from scripts.semantic_understanding import parse_news
result = parse_news("TSMC announces 3nm expansion with $12B capex...")
# 输出：headline/summary/event_type/affected_tickers/impact/investment_idea
```

### 2. 舆情分析 (`parse_sentiment`)
```python
from scripts.semantic_understanding import parse_sentiment
result = parse_sentiment("NVDA gonna crush it. AI demand is infinite.", author="reddit_user")
# 输出：sentiment/sentiment_score/key_claims/factual_vs_speculative/investment_relevance
```

### 3. 财报解读 (`parse_earnings`)
```python
from scripts.semantic_understanding import parse_earnings
result = parse_earnings("Q4 revenue $14.2B (+15% YoY), EPS $2.10 vs $1.98 est...")
# 输出：beat_miss/revenue_guidance/key_highlights/concerns/investment_conclusion
```

### 4. Serenity推文解析 (`parse_serenity`)
```python
from scripts.semantic_understanding import parse_serenity
result = parse_serenity("$SIVE confirmed as primary light source for 1.6T CPO. Chokepoint: InP substrate...")
# 输出：supply_chain_position/chokepoint_type/core_logic/mentioned_tickers/investment_idea
```

## 获取Serenity推文

### 方案A：Nitter RSS（部分实例可用）
```python
from scripts.semantic_understanding import get_serenity_tweets
tweets = get_serenity_tweets(since_hours=48)  # 返回最近48小时推文
```
- `nitter.net/aleabitoreddit/rss` — 有时可用（返回200但内容为空）
- 其他实例：`nitter.privacydev.net`/`nitter.poast.org` — 常被屏蔽

### 方案B：Jina Reader（读整个页面）
```bash
# 获取Serenity主页（含推文列表）
curl -s "https://r.jina.ai/https://x.com/aleabitoreddit" | head -100
```
返回profile信息+推文摘要，非完整推文内容（JS渲染限制）。

### 方案C：手动转发（最可靠）
虎哥在X上看到Serenity推文 → 转发到芝麻QQ → 芝麻调用`parse_serenity()`解析

### 方案D：RSS.app（需注册，免费 tier）
- https://rss.app/rss-feed/create-twitter-rss-feed
- 输入 `https://x.com/aleabitoreddit` → 生成RSS URL → 周期性拉取

## 批量分析Serenity

```python
from scripts.semantic_understanding import analyze_serenity_recent, save_analysis

results = analyze_serenity_recent()  # 获取+解析最近48小时推文
save_analysis(results, "serenity")   # 保存到 logs/semantic_serenity_YYYYMMDD_HHMMSS.json
```

## 关键发现（经验教训）

### Ollama JSON格式陷阱
**问题**：Ollama输出中包含`\{`的JSON schema在Python `.format()`时会触发`KeyError`。
**原因**：Python的`str.format()`把`\{`解释为转义花括号，等价于`{`触发占位符解析。
**解决方案**：不要把JSON schema放在`.format()`的字符串里。用**独立变量存储schema**，直接拼接进prompt。

```python
# ❌ 错误：会触发KeyError
prompt = "输出JSON：\{'key': 'value'\}".format(content=content)

# ✅ 正确：schema作为独立变量，单独拼接
schema = "\{'key': 'value'\}"
prompt = f"输出JSON：\n\n{schema}\n\n内容：\n{content}"
```

### Nitter RSS 全面失效（2026-05实测）
所有公开实例均不可靠：
| 实例 | 状态 |
|------|------|
| nitter.net | 200但内容为空 |
| nitter.privacydev.net | 连接超时 |
| nitter.poast.org | 403 Forbidden |
| nitter.fly.dev | 连接超时 |
| x.excaine.net | 连接超时 |
| twstalker.com | 403 Forbidden |

**最终方案**：虎哥手动转发 + Jina Reader降级读取（只能获取静态内容，不完整）

### Ollama模型状态
- `llama3.2:3b` ✅ 运行正常（已加载）
- `qwen2.5:1.5b-instruct` 未拉取

## 快速测试命令

```bash
cd /root/venv_zhima && python3 scripts/semantic_understanding.py
```

## 验证结果（2026-05-23）

✅ Ollama `llama3.2:3b` 运行正常（PID: 566945）
✅ 新闻解析正常
✅ Serenity推文解析正常
✅ 所有四大解析器均通过测试

**注意**：Nitter RSS 在2026年不稳定，所有公开实例均失效或返回空内容。

**最可靠方案**：虎哥手动转发Serenity链接 → 芝麻用Jina Reader读取 → `parse_serenity()`解析

## 快速测试命令

```bash
cd /root/venv_zhima && python3 scripts/semantic_understanding.py
```

## 已知限制

- Nitter RSS：所有公开实例（nitter.net/nitter.privacydev.net/nitter.poast.org/nitter.fly.dev）均不可靠
- Jina Reader：无法执行JS，只能获取静态内容，X/Twitter页面JS渲染导致内容不完整
- 免费RSS服务（rsshub.app等）：限制严格，不适合生产环境
- **最佳方案：虎哥手动转发Serenity推文链接 → 芝麻解析**

## 文件位置

```
/root/venv_zhima/scripts/semantic_understanding.py  — 主模块
/root/venv_zhima/logs/semantic_*.json               — 解析结果存档
/root/ollama.log                                   — Ollama日志
```