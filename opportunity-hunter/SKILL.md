---
name: opportunity-hunter
description: "主动发现市场机会：X博主语义分析+候选股狩猎引擎。触发词：'主动发现机会'/'狩猎'/'分析X推文'/'技能：opportunity-hunter'"
metadata:
  homepage: https://github.com/virattt/dexter
  allowed-tools: []
---

# Opportunity Hunter - 芝麻主动狩猎引擎 v2

X博主推文分析 + 窭口股候选池管理 + **自动交易信号执行**。

> 架构参考: [Dexter](https://github.com/virattt/dexter)（Virattt的金融研究Agent）
> - 推理日志借鉴自Dexter Scratchpad设计
> - 工具限流软限制警告借鉴自Dexter ToolLimit机制

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
追踪止盈止损（V22原有机制）
```

## 数据源

| 来源 | 工具 | 内容 | 状态 |
|------|------|-------|------|
| **syndication.twitter.com** | x_hunter.py | 完整推文JSON，~100条/博主 | ✅ 主数据源（IP限流） |
| **fxtwitter.com** | 备用 | 单条推文完整内容 | ✅ 备用（限流时用） |
| twiscan.com | 备用 | $代码+截断上下文 | ⚠️ 备用 |
| 硬编码SI库 | scan_short_squeeze.py | 高做空比例股 | ✅ |

### ⚠️ syndication rate limit 说明

syndication.twitter.com 是IP级别的限流，实测：
- 新IP/间隔请求: 前几次正常（aleabitoreddit实测183条推文）
- 短时间多博主连续拉取: "Rate limit exceeded"
- 恢复时间: 几分钟到几小时

**应对策略**：
1. 每批次请求间隔10秒以上，避免连续拉取
2. 触发限流后，用 fxtwitter 单条读取具体推文
3. twiscan.com 备用（数据截断但无需认证）

## 语义分析逻辑

| 语境 | 判断 | 信号类型 |
|------|------|---------|
| "short interest is high" + "$SIVE" | 轧空机会=利好 | LONG_SI |
| "shorts are underwater" + "$JBL" | 空头被套=利好 | LONG_SQ |
| "I cut some exposure" + "$LITE" | 她减仓=看空 | BEARISH_CUT |
| "monopoly over SOI" + "$AXTI" | 窭口垄断=利好 | LONG |
| "short" 单独出现 | 标准做空信号 | BEARISH |

## 信号分级（决定仓位和止损）

| 信号类型 | 来源 | 仓位 | 止损 | 目标 |
|---------|------|------|------|------|
| **LONG_SI**（轧空）| 高SI%+做空者被套 | 5%资金 | 10% | +40% |
| **LONG_SQ**（空头溺水）| 做空者水下 | 5%资金 | 10% | +40% |
| **LONG**（强逻辑）| 窭口垄断+产业逻辑 | 3%资金 | 8% | +25% |

## 监控博主（已验证可用）

> 来源: @panexorcist 推荐 + 芝麻验证

| 用户名 | 专长 | syndication |
|--------|------|------------|
| aleabitoreddit (Serenity) | AI/半导体窭口+轧空 | ✅ |
| morganhousel | 《金钱心理学》作者，投资心法 | ✅ 104条 |
| BrianFeroldi | 财报分析+估值教学 | ✅ 99条 |
| LizAnnSonders | Charles Schwab首席策略师 | ✅ 101条 |
| 10kdiver | 复利/概率长线程教育 | ✅ 100条 |
| charliebilello | 市场数据/ETF统计 | ✅ 104条 |
| awealthofcs (Ben Carlson) | 长期理性投资 | ✅ 103条 |
| elerianm (Mohamed El-Erian) | 经济学家/宏观 | ✅ 101条 |
| ritholtz (Barry Ritholtz) | 市场洞见/反共识 | ✅ 111条 |
| alphatrends (Brian Shannon) | 技术分析趋势 | ✅ 103条 |
| Scottrades | 波段交易实战 | ✅ 105条 |
| ripster47 | 每日交易回顾 | ✅ 29条 |
| MarioNawfal | M&A/AI/全球宏观 | ⚠️ rate limit严格 |

## 关键文件

- 候选池: `/root/venv_zhima/data/opportunity_hunting/hunting_candidates.json`
- 推理日志: `/root/venv_zhima/data/scratchpad/`（JSONL per扫描）
- 财务缓存: `/root/venv_zhima/data/financial_cache/`
- 交易信号: `/root/venv_zhima/data/hunting_signals.json`
- 财务分析: `/root/venv_zhima/scripts/financial_analyzer.py`
- 流水线: `/root/venv_zhima/scripts/hunting_pipeline.py`
- 语义分析: `/root/venv_zhima/scripts/x_hunter.py`
- 狩猎引擎: `/root/venv_zhima/scripts/opportunity_hunting.py`
- 信号管理: `/root/venv_zhima/scripts/hunting_signals.py`
- 推理日志: `/root/venv_zhima/scripts/reasoning_log.py`

## 当前信号池

| 股票 | 类型 | 止损 | 目标 | 逻辑 |
|------|------|------|------|------|
| HIMS | LONG_SI | 90% | 140% | 42%SI+72%毛利率+ROE23.7% |
| SPRB | LONG | 85% | 200% | 目标价$500，罕见病ERT |
| AEVA | LONG_SQ | 92% | 125% | shorts underwater轧空 |

## 借鉴Dexter的设计

| 来自Dexter | 芝麻实现 |
|-----------|---------|
| Scratchpad推理日志 | `reasoning_log.py` → `data/scratchpad/` |
| 工具限流软限制 | 每工具≤3次，超时警告不阻止 |
| 财务分析(get_financials) | `financial_analyzer.py` → analyze_opportunity() |
| 关键指标快照(get_key_ratios) | get_key_ratios() → PE/ROE/毛利率/成长率 |
| 损益表/现金流量表 | get_income_statements() / get_cashflow() |
| 股票筛选器 | screen_stocks() 按财务条件筛选 |

## 使用方式

**手动运行流水线**：
```bash
cd /root/venv_zhima && python3 scripts/hunting_pipeline.py
```

**财务分析单股**：
```bash
python3 /root/venv_zhima/scripts/financial_analyzer.py <ticker>
```

**添加新博主**（在x_hunter.py中修改TRACKED_ACCOUNTS）：
```python
TRACKED_ACCOUNTS = [
    {"username": "aleabitoreddit", "name": "Serenity", "tags": ["AI/半导体", "窭口", "轧空"]},
    {"username": "morganhousel", "name": "Morgan Housel", "tags": ["投资心法", "市场心理学"]},
]
```

## 限制
- syndication接口rate limit严格（IP级别），需控制请求频率
- 实时性依赖虎哥转发推文链接
- xurl未认证，无法主动拉取X时间线