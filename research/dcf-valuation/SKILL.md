---
name: dcf-valuation
description: DCF估值技能 — 8步结构化内在价值分析。当用户问"值多少"、"内在价值"、"低估/高估"、"目标价"、"估值"时触发。
tags: [dcf, valuation, fundamental, intrinsic-value, buffett]
last_updated: 2026-05-23
derived_from: virattt/dexter dcf-skill
---

# DCF估值技能 v1.0

源自Dexter Financial Research Agent的DCF skill，8步结构化估值流程。

## 核心原则

> *"Every model is wrong. Some are useful."* — Dexter / 芒格
> 估值不是精确科学，是思考框架。输出敏感性分析，而非单一数字。

## 8步工作流

```
DCF分析进度：
- [ ] Step 1: 收集财务数据
- [ ] Step 2: 计算FCF增长率
- [ ] Step 3: 估算折现率（WACC）
- [ ] Step 4: 预测未来现金流（1-5年 + 终值）
- [ ] Step 5: 计算现值和每股内在价值
- [ ] Step 6: 敏感性分析
- [ ] Step 7: 验证结果
- [ ] Step 8: 输出结果（含警示）
```

## Step 1: 收集财务数据

### 1.1 现金流历史（5年）
查询: `"[TICKER] annual cash flow statements for last 5 years"`
提取: `free_cash_flow`, `net_cash_flow_from_operations`, `capital_expenditure`
备选: `free_cash_flow = net_cash_flow_from_operations - capital_expenditure`

### 1.2 财务指标快照
查询: `"[TICKER] financial metrics snapshot"`
提取: `market_cap`, `enterprise_value`, `free_cash_flow_growth`, `revenue_growth`, `return_on_invested_capital`, `debt_to_equity`, `free_cash_flow_per_share`

### 1.3 资产负债表
查询: `"[TICKER] latest balance sheet"`
提取: `total_debt`, `cash_and_equivalents`, `current_investments`, `outstanding_shares`

### 1.4 当前股价
查询: `"[TICKER] price snapshot"`
提取: `price`

### 1.5 公司基本信息
查询: `"[TICKER] company facts"`
提取: `sector`, `industry`, `market_cap`

## Step 2: 计算FCF增长率

计算5年FCF CAGR，并与`free_cash_flow_growth`和`revenue_growth`交叉验证。

**增长率选择规则**:
- 历史FCF稳定 → 用CAGR，折扣10-20%
- 上限**15%**（持续更高增长极罕见）

## Step 3: 估算折现率（WACC）

### WACC公式
```
WACC = (E/V)×Re + (D/V)×Rd×(1-T)
E = 股权市值, D = 债务市值, V = E+D
Re = 股权成本 = Rf + β×ERP
Rd = 债务成本（税前）
T = 税率
```

### 默认假设
| 参数 | 默认值 |
|------|--------|
| 无风险利率 (Rf) | 4% |
| 股权风险溢价 (ERP) | 5-6% |
| 债务成本（税前）| 5-6% |
| 税率 | 30% |

### 行业WACC参考

| 行业 | 基准WACC |
|------|----------|
| 科技（大盘）| 8-10% |
| 半导体 | 10-12% |
| 金融 | 7-9% |
| 消费 | 7-9% |
| 医药 | 8-10% |
| 工业 | 8-10% |

**合理性检验**: WACC应比`return_on_invested_capital`低2-4%（价值创造公司）

## Step 4: 预测未来现金流

### Year 1-5
增长率每年衰减5%（反映竞争动态）：
- Year 1: FCF × (1 + g)
- Year 2: FCF × (1 + g×0.95)
- Year 3: FCF × (1 + g×0.90)
- Year 4: FCF × (1 + g×0.85)
- Year 5: FCF × (1 + g×0.80)

### 终值（Terminal Value）
Gordon Growth Model:
```
TV = FCF_5 × (1 + g_t) / (WACC - g_t)
g_t = 2.5%（GDP增速代理）
```

## Step 5: 计算现值

```
PV = Σ FCF_t / (1+WACC)^t  (t=1 to 5)
PV_TV = TV / (1+WACC)^5
EV = ΣPV + PV_TV
Net Debt = total_debt - cash
Equity Value = EV - Net Debt
Fair Value Per Share = Equity Value / outstanding_shares
```

## Step 6: 敏感性分析

3×3矩阵：WACC（基准±1%）vs 终值增长率（2.0%, 2.5%, 3.0%）

```
          终值增长率
WACC      2.0%    2.5%    3.0%
9%        [x]     [x]     [x]
10%       [x]     [基准]  [x]
11%       [x]     [x]     [x]
```

## Step 7: 验证结果

| 检验项 | 规则 | 失败处理 |
|--------|------|----------|
| EV对比 | 计算EV应在报告EV±30%内 | 重调WACC或增长率 |
| 终值占比 | 终值应占总EV的50-80%（成熟公司） | 增长率可能过高（>90%）或过低（<40%） |
| 每股交叉验证 | `FCF_per_share × 15-25` 作为快速检验 | — |

验证失败 → 重新审视假设

## Step 8: 输出格式

### 估值总结
```
当前股价: $X
内在价值: $Y
上涨/下跌: +Z%
```

### 关键输入表
| 参数 | 值 | 来源 |
|------|-----|------|
| FCF增长率 | X% | 历史CAGR，折扣15% |
| WACC | X% | 行业基准 + β调整 |
| 终值增长率 | X% | 2.5%（GDP代理） |
| ... | ... | ... |

### FCF预测表
| 年份 | FCF | 折现系数 | PV |
|------|-----|----------|-----|
| 1 | $X | 0.926 | $X |
| ... | ... | ... | ... |

### 敏感性矩阵
（见Step 6）

### 警示（Caveats）
- DCF局限：依赖假设，敏感性高
- 公司特有风险：[具体风险]
- 模型局限性：[具体局限]

## 使用场景

触发词：`值多少`、`内在价值`、`低估/高估`、`目标价`、`DCF`、`估值`、`fair value`、`intrinsic value`

调用方式：
```python
# 伪代码，芝麻用Alpaca数据+新闻构建
from scripts.dcf_builder import run_dcf
result = run_dcf("NVDA")
# 返回：内在价值、敏感性矩阵、关键假设、警示
```

## 数据源

- Alpaca Market Data API（实时价格）
- Financial Datasets API 或 Alpha Vantage（财务报表）
- 新闻事件基本面判断（语义理解模块辅助）

## 已知限制

- 需要盈利且FCF为正的公司（非亏损/初创）
- 周期性行业需额外调整
- 并购情境不适用（控制溢价难以量化）

## 文件位置

```
/root/venv_zhima/scripts/dcf_builder.py   — DCF构建器（待实现）
/root/venv_zhima/logs/dcf_*.json          — DCF分析结果存档
```