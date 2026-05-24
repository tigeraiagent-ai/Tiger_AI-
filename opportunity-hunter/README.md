# Opportunity Hunter v2

芝麻主动狩猎引擎：X博主语义分析 + 窭口股候选池 + 自动交易信号执行。

## 核心架构（闭环）

```
每小时cron → hunting_pipeline.py
  ↓
x_hunter.py → syndication.twitter.com抓取完整推文
  ↓
语义分析 → 判断LONG_SI/LONG_SQ/LONG/BEARISH
  ↓
hunting_signals.py → 生成精选交易信号
  ↓
auto_trade_executor.py → 自动市价买入
  ↓
追踪止盈止损
```

## 监控博主

| 用户名 | 专长 |
|--------|------|
| aleabitoreddit (Serenity) | AI/半导体窭口+轧空 |
| MarioNawfal | M&A/AI/全球宏观 |

## 信号分级

| 类型 | 仓位 | 止损 | 目标 |
|------|------|------|------|
| LONG_SI（轧空）| 5% | 10% | +40% |
| LONG_SQ（空头溺水）| 5% | 10% | +40% |
| LONG（强逻辑）| 3% | 8% | +25% |

## 当前信号池

| 股票 | 类型 | 止损 | 目标 | 逻辑 |
|------|------|------|------|------|
| HIMS | LONG_SI | 90% | 140% | 42%SI+72%毛利率+ROE23.7% |
| SPRB | LONG | 85% | 200% | 目标价$500，罕见病ERT |
| AEVA | LONG_SQ | 92% | 125% | shorts underwater轧空 |

## 目录结构

```
opportunity-hunter/
├── SKILL.md         完整技能文档
├── README.md        本文件
├── x_bloggers.md    X博主监控清单
├── references/
│   ├── dexter_research.md   Dexter架构研究
│   └── chokepoint_logic.md  窭口分析逻辑
└── scripts/
    ├── opportunity_hunting.py   狩猎引擎核心
    ├── x_hunter.py             X博主语义分析
    ├── hunting_signals.py      交易信号管理
    ├── hunting_pipeline.py     完整流水线
    ├── financial_analyzer.py   财务分析
    └── reasoning_log.py        推理日志
```

## 使用

```bash
cd /root/venv_zhima && python3 scripts/hunting_pipeline.py
```

## 架构借鉴

参考 [Dexter](https://github.com/virattt/dexter) 设计：
- Scratchpad推理日志
- 工具限流软限制
- 财务分析模块

## 发布信息

- Repo: github.com/tigeraiagent-ai/Tiger_AI-
- 分支: main
- 技能路径: opportunity-hunter/SKILL.md