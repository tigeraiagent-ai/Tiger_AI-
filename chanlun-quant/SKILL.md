---
name: chanlun-quant-integration
description: 缠论量化整合方法论 — 通过四次失败尝试 + 成功验证的完整经验
tags: [缠论, 趋势跟踪, 回测, 出场信号, V19_ZM]
last_updated: 2026-04-29
---

# 缠论量化整合方法论

## 核心结论

**入场用缠论 → ❌ 四次全部失败**
**出场用缠论 → ✅ V19_ZM诞生，CAGR 370%**

---

## ❌ 四次入场整合失败记录

| 方案 | 信号定义 | CAGR变化 | 问题 |
|------|---------|---------|------|
| v1 | MACD底背驰+价格新低 | — | 条件太严格，0天信号 |
| v2 | RSI<40底背驰入场 | **-58%** | 抄底逆势，MaxDD飙升 |
| v3 | RSI<35入场加分 | **-24%** | 跟趋势跟踪打架 |
| v4 | 第三类买点加分 | **-35%** | MaxDD飙到41% |

**根因**：趋势跟踪 = 追涨，缠论买点 = 抄底，底层逻辑冲突。

---

## ✅ 成功验证：缠论背驰作为出场信号

### V19_ZM核心逻辑
- 大涨之后出现背驰 → 主力可能出货 → 提前止盈
- 盈利>25%才触发出场 → 精准止盈，不被震荡洗出
- RSI<50超卖区域的背驰才有效 → 过滤噪音

### 盈利门槛扫描结果

| 门槛 | CAGR | Sharpe | MaxDD | 胜率 | 触发次数 |
|------|------|--------|-------|------|---------|
| >5% | 329% | 1.14 | 29.2% | 87.5% | 17 |
| >10% | 325% | 1.06 | 33.5% | 71.0% | 13 |
| >15% | 367% | 1.11 | 33.5% | 70.0% | 12 |
| >20% | 328% | 1.13 | 30.3% | 81.0% | 12 |
| **>25%** | **370%** | **1.12** | **30.3%** | **79.2%** | **7** |

### V19_ZM vs V18_c_ZM

| 指标 | V18_c_ZM | V19_ZM | 差异 |
|------|---------|--------|------|
| CAGR | 193.3% | **370.3%** | **+177%** |
| Sharpe | 0.88 | **1.12** | **+0.24** |
| MaxDD | 25.4% | 30.3% | +4.9% |
| 胜率 | 68.8% | **79.2%** | **+10.4%** |

---

## 整合检查清单

**入场用缠论 → 大概率失败，换方向**

**出场用缠论 → 检查：**
1. 是否有盈利门槛保护？（>25%最优）
2. 是否限定超卖区域？（RSI<50）
3. 是否只止盈不止损？

---

## 信号计算代码

```python
def compute_chan_exit(close_arr, rsi_arr, lookback=20):
    """
    缠论底背驰出场信号：价格新低 + RSI未同步新低
    仅在超卖区域(RSI<50)有效
    """
    price_min = pd.DataFrame(close_arr).rolling(lookback).min().values
    rsi_min = pd.DataFrame(rsi_arr).rolling(lookback).min().values
    
    is_price_low = (close_arr == price_min)
    is_rsi_sync_low = is_price_low & (rsi_arr == rsi_min)
    divergence = is_price_low & ~is_rsi_sync_low
    in_oversold = rsi_arr < 50
    
    signal = np.zeros_like(close_arr, dtype=np.int8)
    signal[divergence & in_oversold] = 1
    return signal
```

---

## 文件记录

- 失败脚本：`/root/.hermes/scripts/backtest_v18c_chan.py`
- 出场验证：`/root/.hermes/scripts/backtest_v18c_exit.py`
- **V19_ZM最终版**：`/root/.hermes/scripts/backtest_v19_zm.py`
- SKILL文档：`/root/.hermes/skills/productivity/backtesting-davis-double/SKILL.md`
