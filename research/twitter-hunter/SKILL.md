---
name: twitter-hunter
description: Twitter狩猎引擎 — 无API key抓取16个关注账号推文，Jina Reader降级 + Ollama语义分析找投资机会。交易时段ET 9:00自动执行，有机会才推送。
trigger: 每交易日ET 9:00 自动触发，或虎哥说"扫一下Twitter"
last_updated: 2026-05-23
tags: [twitter, hunting, social-media, jina, ollama, opportunity]
derived_from: virattt/dexter + twitter syndication endpoint
---

## 概述

Twitter狩猎引擎是芝麻的**主动感知系统**，自动抓取16个高质量投资博主的推文，通过Ollama语义分析发现非共识投资机会。

**完全自主**：发现信号 → 自主决策 → 自主执行，虎哥静默接收。

## 架构

```
twitter syndication endpoint
  ↓ (https://syndication.twitter.com/srv/timeline-profile/screen-name/{user})
HTML + __NEXT_DATA__ JSON
  ↓ 解析timeline entries
推文列表（每账号~100条）
  ↓ 24h缓存
去重 → 新推文过滤
  ↓ Ollama语义分析
投资机会检测
  ↓ 置信度≥0.7
芝麻自主买入 Alpaca Paper
  ↓ 无机会
完全静默
```

## 数据源方案

| 方案 | 状态 | 说明 |
|------|------|------|
| **Twitter syndication** | ✅ 主力 | `syndication.twitter.com` 返回嵌入JSON，每账号最多100条，24h缓存 |
| **Jina Reader** | ✅ 降级 | 单条推文内容提取，syndication失败时用 |
| **Nitter RSS** | ❌ 失效 | 所有公开实例已下线或限流 |
| **RSS.app** | ❌ 需付费 | API key收费 |

## 关注账号清单

### P0 — 供应链瓶颈 & 反向研究

| 账号 | 定位 | 内容方向 |
|------|------|----------|
| **@aleabitoreddit** (Serenity) | 前RISC-V基金会成员，前AI研究科学家 | AI/半导体供应链瓶颈，chokepoint，1年630%+回报 |
| **@Contrary_Res** | Contrary Research，反向投资 | 发现非共识深度研究，逆向思维 |

### P1 — 技术分析 & 价值投资 & 宏观

| 账号 | 定位 | 内容方向 |
|------|------|----------|
| **@alphatrends** (Brian Shannon CMT) | 30年技术分析专家 | SPY/QQQ/SMH每日分析，支撑阻力，期权教育 |
| **@TheValueist** | 价值+供应链chokepoint | InP/CPO等关键材料分析，图表+基本面结合 |
| **@morganhousel** | 《The Psychology of Money》作者 | 市场心理学，长期投资智慧 |
| **@LizAnnSonders** | Charles Schwab首席策略师 | 数据驱动宏观分析，专业中立 |
| **@awealthofcommonsense** (Ben Carlson) | 理性长期投资 | 幽默、理性的投资视角 |
| **@ritholtz** (Barry Ritholtz) | Bloomberg资深作者 | 市场洞见，反共识观点 |
| **@elerianm** (Mohamed El-Erian) | 诺贝尔经济学奖得主 | 宏观经济与股市深度评论 |

### P2 — 宏观预警 & AI投资

| 账号 | 定位 | 内容方向 |
|------|------|----------|
| **@zerohedge** | 宏观/系统性风险 | 极端空头，风险事件预警 |
| **@DeItaone** | 新闻速报 | Bloomberg快讯，即时市场新闻 |
| **@aleximm** | AI投资研究 | AI对应用软件影响分析 |
| **@a1research__** | AI+DeFi前沿 | Agent/DeFi前沿研究 |
| **@OrnnExchange** | AI芯片供应链 | 计算商品化，供应链集中度 |
| **@techinsightsinc** | 半导体行业数据 | 行业数据，瓶颈报告 |

## 执行脚本

```bash
# 完整狩猎（含Ollama语义分析）
python3 /root/venv_zhima/scripts/twitter_hunter.py --analyze

# 仅抓取（不做语义分析，快速检查新推文）
python3 /root/venv_zhima/scripts/twitter_hunter.py
```

## 决策阈值

| 置信度 | 动作 |
|--------|------|
| ≥0.7 | 芝麻自主买入Alpaca Paper（5%试探仓） |
| 0.5-0.7 | 降级观察池，持续跟踪 |
| <0.5 | 忽略 |

## 缓存策略

- 每个账号每24小时最多抓取1次（避免syndication限流）
- 缓存路径：`/root/venv_zhima/logs/hunter/cache/{username}.json`
- 新推文通过ID去重对比历史

## 输出格式

```json
{
  "scan_time": "2026-05-23T09:00:00",
  "accounts": 16,
  "total": 1240,
  "new": 3,
  "opportunities": [
    {
      "screen_name": "aleabitoreddit",
      "symbols": ["NBIS", "IREN"],
      "confidence": 0.82,
      "type": "供应链瓶颈",
      "summary": "NBIS微软合同利润率比IREN高40%，normalized to 300MW",
      "link": "https://x.com/aleabitoreddit/status/..."
    }
  ]
}
```

## 技术细节

### Twitter syndication endpoint（主力方案）

```
GET https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}
Headers: User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)
         Accept: application/json, text/html
```

返回HTML，其中`<script id="__NEXT_DATA__">`包含完整timeline JSON：
```python
import re, json, requests

def extract_tweets_via_syndication(username):
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    r = requests.get(url, timeout=15, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "Accept": "application/json, text/html"
    })
    if r.status_code == 200:
        # 解析__NEXT_DATA__
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">([\s\S]+?)</script>', r.text)
        if m:
            data = json.loads(m.group(1))
            return data["props"]["pageProps"]["timeline"]["entries"]
    return []
```

**关键发现（2026-05-23）**：
- syndication返回完整timeline（@aleabitoreddit实测99条）
- ⚠️ 有rate limit：连续请求返回429 "Rate limit exceeded"
- **解决：24小时缓存**（每个账号每24h最多抓取1次，缓存写入`/root/venv_zhima/logs/hunter/cache/{username}.json`）

### Jina Reader降级方案（单推文）

```python
def jina_fetch_tweet(screen_name, status_id):
    url = f"https://r.jina.ai/https://x.com/{screen_name}/status/{status_id}"
    r = requests.get(url, headers={"Accept": "text/markdown"})
    return r.text  # 返回Markdown格式
```

### 已验证失败方案

| 方案 | 状态 | 原因 |
|------|------|------|
| Nitter RSS | ❌ 失效 | 所有公开实例已下线（nitter.net/nitter.privacydev.net均不可用） |
| rss.app | ❌ 需付费 | API key收费 |
| rsshub.app | ❌ 失效 | X平台封禁第三方抓取 |
| Jina直接读X主页 | ❌ 内容不完整 | X页面JS渲染，Jina无法获取完整内容 |
| Twitter Atom feed | ❌ 重定向HTML | x.com/{user}/rss返回268KB HTML，非XML |

### Ollama语义分析

```python
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def ollama(prompt, system="", temp=0.3):
    r = requests.post(OLLAMA_URL, json={
        "model": "llama3.2:3b",
        "prompt": prompt,
        "system": system,
        "stream": False
    }, timeout=120)
    return r.json().get("response", "").strip()
```

### 24h缓存策略

```python
def is_cache_fresh(username, max_age_hours=24):
    cache_file = f"/root/venv_zhima/logs/hunter/cache/{username}.json"
    try:
        with open(cache_file) as f:
            last_fetch = datetime.fromisoformat(json.load(f)["last_fetch"])
            return (datetime.now() - last_fetch).total_seconds() / 3600 < max_age_hours
    except:
        return False
```

### 验证命令

```bash
# 测试单一账号抓取
cd /root/venv_zhima && python3 -c "
from scripts.twitter_hunter import fetch_via_syndication
tweets, rl = fetch_via_syndication('aleabitoreddit')
print(f'OK: {len(tweets)}条' if tweets else f'Rate limited: {rl}')
"

# 完整狩猎
python3 /root/venv_zhima/scripts/twitter_hunter.py --analyze
```

### 已知限制

- syndication rate limit：同一IP大量请求后全天429（缓存解决）
- Jina Reader无法抓取X主页timeline（只能单推文）
- 所有Nitter实例已失效
- 无免费方案获取转推/回复（只有timeline内嵌推文）

## cron调度

| 时间 | 任务 |
|------|------|
| 每日 ET 9:00 | Twitter狩猎引擎完整扫描（置信度≥0.7时自主执行交易） |
| 每日 ET 9:00 | 市场多维度扫描（持仓股票新闻） |

## 文件位置

```
/root/venv_zhima/scripts/twitter_hunter.py    # 主脚本
/root/venv_zhima/scripts/twitter_hunt_cron.sh  # cron入口
/root/venv_zhima/logs/hunter/cache/          # 每账号缓存
/root/venv_zhima/logs/hunter/hunt_*.log     # 执行日志
```