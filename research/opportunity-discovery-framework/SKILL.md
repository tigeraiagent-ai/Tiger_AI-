---
name: opportunity-discovery-framework
description: 主动狩猎引擎 — 主动发现投资机会的系统方法论。数据→信号→决策→执行，芝麻完全自主闭环。覆盖供应链瓶颈/轧空/宏观/财报/期权异常/跨市场联动六大类型。
trigger: 每日盘中监控 + 虎哥转发 + 周末深度研究
last_updated: 2026-05-23
tags: [hunting, opportunity-discovery, supply-chain, momentum, macro, earnings, options, cross-market]
---

# 主动狩猎引擎 v2.0

> **核心定位**：狩猎引擎 = 芝麻的感知系统
> 数据 → 信号 → 决策 → 执行，全部闭环自主完成
> 虎哥只接收结果，不参与过程

---

## 一、闭环架构

```
狩猎（感知）
  ↓ 抓取数据（Twitter/新闻/舆情）
语义理解（大脑）— Ollama本地LLM
  ↓ 解析结构化机会
策略引擎 V21_ZM（决策）
  ↓ 信号 + 策略验证
Alpaca Paper（执行）
  ↓ 买入/卖出
结果 → 复盘 → 学习 → 狩猎优化
```

---

## 二、狩猎目标 & 数据源

| 优先级 | 狩猎目标 | 数据来源 | 频率 | 时效 |
|--------|----------|----------|------|------|
| 🔴 P0 | 供应链瓶颈 | Twitter博主（见Section三）| 虎哥转发/按需 | 1-3个月 |
| 🔴 P0 | 持仓标的重要新闻 | Alpaca News API | 每交易日9:00 | 短期催化 |
| 🟡 P1 | 轧空机会扫描 | scan_short_squeeze.py | 每周五收盘 | 1-4周 |
| 🟡 P1 | 财报超预期 | 语义理解财报解析 | Q1/Q2/Q3/Q4密集 | 即时 |
| 🟢 P2 | X舆情异动 | Twitter博主（虎哥转发）| 按需 | 7天内 |

---

## 三、Twitter博主关注清单

### P0 — 最高价值（供应链瓶颈 & 反向研究）

| 账号 | 定位 | 内容方向 | 获取方式 |
|------|------|----------|----------|
| **@aleabitoreddit** (Serenity) | 前RISC-V Foundation，前AI研究科学家 | AI/半导体供应链chokepoint，2-3层瓶颈分析 | 虎哥转发 |
| **@Contrary_Res** | Contrary Research团队 | 反向研究，非共识深度标的 | 虎哥转发 |

### P1 — 高价值（技术面补充 & 供应链细化）

| 账号 | 定位 | 内容方向 | 获取方式 |
|------|------|----------|----------|
| **@alphatrends** (Brian Shannon CMT) | 技术分析，30年经验 | SPY/QQQ/SMH每日分析，支撑阻力，期权教育 | RSS.app生成feed |
| **@TheValueist** | 价值投资+供应链 | InP/CPO等关键材料chokepoint | 虎哥转发 |
| **@NuttyCLD** | 供应链+韩国半导体 | Korea AI半导体被低估逻辑 | 虎哥转发 |

### P2 — 补充（宏观预警 & AI投资逻辑）

| 账号 | 定位 | 内容方向 | 获取方式 |
|------|------|----------|----------|
| **@zerohedge** | 宏观/系统性风险 | 极端空头，风险事件预警 | RSS.app |
| **@DeItaone** | 新闻速报 | Bloomberg/Earnings快讯 | RSS.app |
| **@aleximm** | AI投资研究 | AI对应用软件影响研究 | 虎哥转发 |
| **@a1research__** | AI+DeFi前沿 | Agent/DeFi/基础设施研究 | 虎哥转发 |
| **@OrnnExchange** | 计算商品化 | AI芯片供应链集中度分析 | 虎哥转发 |

### 行业数据账号

| 账号 | 定位 | 内容方向 | 获取方式 |
|------|------|----------|----------|
| **@techinsightsinc** | TechInsights | 半导体行业数据/瓶颈报告 | 虎哥转发 |
| **@SIAmerica** | 半导体产业协会 | 政策/出口管制/行业数据 | RSS.app |

---

## 四、信号 → 决策阈值

### 触发条件（需同时满足）

- `confidence >= 0.7`（语义解析输出）
- 逻辑非共识（找2-3层供应链瓶颈，不是显而易见）
- 时机信号：SOS / 缠论买点 / VIX择时

### 禁止条件

- VIX > 35：系统性风险，停止主动狩猎
- 单笔潜在亏损 > 总权益5%
- 流动性不足：日均成交<$10M
- 小市值：<$500M（供应链逻辑不适用）

### 狩猎决策流程

```
猎物出现（Twitter/新闻/舆情）
  ↓ 语义理解解析（confidence >= 0.7?）
  ↓ 策略验证（V21_ZM信号? 缠论买点?）
  ↓ 决策（置信度达标 → 执行，否 → 降级观察池）
```

---

## 五、执行标准

| 参数 | 规则 |
|------|------|
| 最大单标仓位 | 总权益10% |
| 首次买入 | 5%（试探） |
| 确认后加仓 | +3%（最多到10%） |
| 止损 | 海龟N值止损（策略已有） |
| 新信号 | 市价单立即执行 |

---

## 六、候选池管理

### 三层结构

| 池 | 时间范围 | 标准 |
|---|----------|------|
| 🔥 热池 | 1个月内触发 | 轧空信号已出现 / 财报临近 / 已有仓位 |
| 📈 观察池 | 1-3个月 | 逻辑成立，等待催化剂 |
| 🔍 研究池 | 3-6个月 | 供应链深度理解，AI辅助分析 |

---

## 七、复盘机制

### 每次交易记录（scratchpad）

```json
{
  "trade_id": "T20260523_001",
  "signal_source": "Twitter/@aleabitoreddit",
  "signal_content": "$SIVE CPO光源 1.6T瓶颈",
  "parse_confidence": 0.82,
  "decision": "BUY",
  "entry_price": 12.50,
  "entry_time": "2026-05-23 10:30 ET",
  "stop_loss": 11.25,
  "size_shares": 100,
  "size_pct_equity": 5,
  "exit_reason": "stop_loss / target / strategy_switch"
}
```

### 周复盘（每周六）

1. **信号来源统计**：哪类狩猎来源命中率高？
2. **胜率 & 盈亏比**：Semantic vs 技术面 vs 持仓跟踪
3. **失败归因**：信号问题 / 执行问题 / 市场问题
4. **狩猎优化**：调整数据源优先级

---

## 八、报告流

| 场景 | 推送给虎哥？ | 内容 |
|------|-------------|------|
| 狩猎到信号并执行 | ❌ 否 | 静默执行 |
| 止损触发 | ✅ 是 | 止损结果 |
| 单笔浮亏>3% | ✅ 是 | 告警 |
| 周报告 | ✅ 是 | 狩猎统计+交易复盘 |
| 持仓标的重大新闻 | ✅ 是 | 新闻摘要+持仓影响 |
| VIX>30 / <15 | ✅ 是 | 仓位调整说明 |

**原则**：无事不推送，有事才说。虎哥静默接收结果。

---

## 九、机会分类体系

### A. 供应链瓶颈（核心）
**特征**：全球1-3家供应商 / 扩产>2年 / 非共识小市值
**路径**：超级趋势→物理供应链拆解→找第二/三层瓶颈→AI交叉验证→仓位

### B. 轧空机会（芝麻已有）
**特征**：SI%>20% / 量比>2x / 板块催化 / 股价低位
**路径**：动物股筛选→SI%排序→量比监控→催化确认→执行

### C. 宏观事件驱动
**特征**：地缘冲突 / 政策突变 / 央行转向 / 监管变化
**路径**：宏观监控→找影响标的→反向推理→快速反应

### D. 财报超预期
**特征**：预期差（市场下调但实际beat）/ 指引超预期
**路径**：财报日历→预披露监控→找预期差→盘前/盘中交易

### E. 期权异常定价
**特征**：IV percentile <20% / 基本面支撑 / 催化剂临近
**路径**：期权链扫描→基本面确认→买入straddle/strangle

### F. 跨市场联动
**特征**：美股→港股/台股ADR映射 / 加密→MSTR联动
**路径**：美股异动→跨市场找同类→联动确认→先行买入

---

## 十、AI辅助投研流程

### 用Ollama做供应链拆解

```python
# 语义理解模块
from scripts.semantic_understanding import parse_serenity, parse_news

# Serenity推文解析
result = parse_serenity("$SIVE confirmed as primary light source for 1.6T CPO. Chokepoint: InP substrate.")
# → 提取：primary_ticker / supply_chain_position / chokepoint_type / investment_idea

# 新闻解析
result = parse_news("TSMC announces 3nm capacity expansion with $12B capex...")
# → 提取：event_type / impact / affected_tickers / investment_idea
```

### Prompt模板（供应链拆解）

```
# 找瓶颈
"如果全球AI数据中心扩张，从GPU→HBM→网络→光模块→衬底→封装，分别卡在哪里？列出瓶颈公司和产能。"

# 找供应商
"光模块产业链中，InP衬底供应商有哪些？上市公司？市值？进入哪些客户供应链？"

# 交叉验证
"AXTI这家公司：1)会被替代吗？2)产能够吗？3)客户验证了吗？4)估值透支几年？"
```

---

## 相关技能

- `semantic-understanding` — 语义理解（新闻/舆情/财报/Serenity推文）
- `dcf-valuation` — DCF 8步估值（基本面验证）
- `x-sentiment-research` — X舆情研究方法
- `agent-scratchpad` — 交易日志记录
- `zhima-paper-trading` — Alpaca执行手册

---

## 文件位置

```
/root/venv_zhima/scripts/semantic_understanding.py  — 语义理解
/root/venv_zhima/scripts/scratchpad.py              — 交易日志
/root/venv_zhima/logs/scratchpad/                    — scratchpad文件
/root/.hermes/skills/research/opportunity-discovery-framework/SKILL.md  — 本技能
```