---
name: x-sentiment-research
description: X/Twitter舆情研究技能 — 分解查询→执行搜索→综合输出结构化简报。当用户问"市场怎么看"、"Twitter sentiment"、"what's CT saying"时触发。
tags: [x, twitter, sentiment, social-media, public-opinion, research]
last_updated: 2026-05-23
derived_from: virattt/dexter x-research-skill + Dexter方法论
---

# X舆情研究技能 v1.0

源自Dexter Financial Research Agent的X Research Skill。结构化Twitter舆情研究方法。

## 核心方法论

> *"X sentiment is not a reliable predictor; sample bias toward vocal minorities."* — Dexter

Twitter舆情是**信号来源，不是预测工具**。核心价值：发现催化因素、识别共识、捕捉早期趋势。

## 研究循环

```
分解查询 → 执行搜索 → 关键账号核查 → 追踪线程 → 综合输出
```

## Step 1: 分解为查询

将研究问题拆解为3-5个针对性查询：

| 查询类型 | 策略 | 示例 |
|----------|------|------|
| **核心查询** | 直接关键词或`$TICKER` | `$NVDA`, `TSMC earnings` |
| **专家声音** | `from:username` | `from:zerohedge` |
| **空头信号** | 负面关键词 | `(overvalued OR bubble OR risk)` |
| **多头信号** | 正面关键词 | `(bullish OR upside OR catalyst)` |
| **新闻/链接** | 加`has:links` | `$NVDA has:links` |
| **降噪** | `-is:reply`专注原创 | `from:AiAnalyst -is:reply` |
| **时间窗口** | `since:"1d"`或`"7d"` | `since:"7d"` |

**组合示例**：
```
$TICKER (bullish OR catalyst) since:"7d" -is:reply has:links min_likes:10
from:SerenityAI since:"1d" -is:reply
```

## Step 2: 执行搜索

使用`x_search`工具（`command: "search"`）：
- 初始: `sort: "likes"`, `limit: 15`
- 宽话题: `min_likes: 5` 过滤噪音
- 时间敏感: `since:"1d"`
- 噪音多: 加更多运算符或提高`min_likes`
- 结果太少: 用`OR`拓宽或移除限制条件

## Step 3: 关键账号核查（可选）

已知分析师/基金经理/高管，用`command: "profile"`直接看近期发帖：

```
# 示例关键账号（加密/AI方向）
Serenity: @aleabitoreddit（供应链瓶颈）
ZeroHedge: @zerohedge（宏观）
The Kobe Letter: @thekobeletter（宏观/大宗）
Chris Bolland: @ChrisBolland（英国宏观）
```

## Step 4: 追踪线程（可选）

高互动推文是线程起点时，用`command: "thread"`+ tweet ID获取完整上下文。

## Step 5: 综合输出

### 输出格式

```
### 查询摘要
研究了[X]，时间窗口[Y]，主要查询[Z]

### 舆情主题

#### [主题1：多头]
[1-2句主题描述]
- @username: "[关键引用]" — [点赞数]♥ [推文链接]
- @username2: "[另一视角]" — [点赞数]♥ [推文链接]

#### [主题2：空头]
[类似结构]

#### [主题3：新闻/催化]
[类似结构]

### 整体舆情
- 主导基调：[多头/空头/混合/中性]
- 信心水平：[高/中/低]
- 机构和散户分歧：[有/无]

### 警示
- X舆情不是可靠预测指标
- 样本偏向声音大的少数群体
- 仅代表过去7天窗口
```

## 调优启发

| 问题 | 解决方案 |
|------|----------|
| 噪音太多 | 提高`min_likes`，加`-is:reply`，收窄关键词 |
| 结果太少 | 用`OR`拓宽，移除限制性运算符 |
| 加密垃圾 | 加`-airdrop -giveaway -whitelist` |
| 只要专家 | 用`from:`或`min_likes:50` |
| 要深度不要热点 | 加`has:links` |

## 芝麻的具体实现

由于芝麻没有X API key，采用以下替代方案：

### 方案A：虎哥转发触发（推荐）
1. 虎哥在X看到相关讨论 → 转发链接给芝麻
2. 芝麻用`jina_read(url)`获取推文内容
3. 芝麻用`parse_serenity()`或`parse_sentiment()`解析
4. 综合成结构化简报

### 方案B：RSS.app（需注册，免费tier）
1. 去 https://rss.app/rss-feed/create-twitter-rss-feed
2. 输入`https://x.com/USERNAME`
3. 获取RSS URL，定期拉取

### 方案C：关键词监控
- 监控$SIVE、$AXTI等核心标的的Twitter讨论
- 虎哥手动转发高价值讨论

## 与语义理解模块的集成

```python
# 虎哥转发推文 → 芝麻解析
from scripts.semantic_understanding import parse_sentiment, parse_serenity

# 舆情分析
result = parse_sentiment(content, author="twitter_user")

# Serenity专用的供应链逻辑解析
serenity = parse_serenity(content)
```

## 文件位置

```
/root/venv_zhima/scripts/semantic_understanding.py  — 包含parse_serenity/parse_sentiment
/root/venv_zhima/logs/sentiment_*.json              — 舆情研究存档
```

## 关键原则

1. **信号不是预测** — Twitter讨论是发现机会的线索，不是交易决策的依据
2. **偏见意识** — 样本偏向声音大的少数人，沉默大多数可能不同意
3. **时间窗口** — 7天内的讨论最具时效性，超过30天价值大幅下降
4. **交叉验证** — Twitter观点需与基本面/技术面交叉验证才能形成交易观点