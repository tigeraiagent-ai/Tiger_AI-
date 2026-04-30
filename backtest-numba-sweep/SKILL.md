---
name: backtest-numba-sweep
version: 1.1
description: Numba加速的美股策略参数扫描框架 - 秒级遍历数百组参数
---

# backtest-numba-sweep

## When to Use
对美股策略做参数扫描优化时使用（>50组参数）。比纯 Python 快 100-1000 倍，135 组参数 1.3 秒跑完。

## File Location
- 脚本: `/root/.hermes/scripts/backtest_v18c_numba.py`
- 结果: `/root/.hermes/scripts/v18c_numba_sweep.csv`

## Python Environment
```bash
# 系统Python 3.12 带 vectorbt + numba
/usr/bin/python3.12

# 注意：hermes-agent venv (Python 3.11) 没有这些包
# terminal() 被 pip 卡住时，用 /usr/bin/python3.12 直接执行脚本文件
```

## Numba JIT 热路径
- Numba 只支持纯 numpy 操作
- 不支持：生成器表达式、yield、pandas rolling().apply
- 用预分配 numpy 数组替代 list，用 np.sum/np.argmax 替代

## Timezone 处理
```python
if closes.index.tz is not None:
    closes.index = closes.index.tz_localize(None)
vix_aligned = vix_df.reindex(closes.index, method='pad')['vix']
```

## 常见错误
1. **TypeError: Cannot compare dtypes datetime64[ns] UTC vs naive** → 统一去时区
2. **UnsupportedError: yield in a closure** → 改用预分配数组（trade_returns = np.zeros(max_trades)）
3. **NameError: vbt not defined** → import vectorbt 在 sys.path.insert 之后
4. **terminal被pip堵**: 不要在terminal里跑pip install，用 `/usr/bin/python3.12` 直接执行脚本文件

## Numba预热
第一次调用JIT函数会自动编译（慢约3-5秒），之后每次调用毫秒级。建议在扫描前先跑一次：
```python
_ = backtest_numba(close_arr[:30], vix_arr[:30], score_arr[:30],
                   weekly_mask[:30], 15.0, 12.0, 48, 4)
```
