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

## 验证结果（2026-05-23）

- ✅ syndication endpoint对@aleabitoreddit可返回99条推文
- ⚠️ syndication有rate limit（每账号每24h上限，缓存设计消除重复请求）
- ⚠️ Jina Reader可抓取单条推文内容（`https://r.jina.ai/https://x.com/{user}/status/{id}`）
- ✅ Ollama llama3.2:3b可正常做语义分析
- ⚠️ 当前被rate limit限制，缓存建立后24h内不再请求

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