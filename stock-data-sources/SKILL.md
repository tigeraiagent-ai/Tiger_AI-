---
name: stock-data-sources
description: 股票数据源优先级 - 从腾讯云VM获取美股数据的经验总结
---
# 股票数据源优先级

## 已验证可用的数据源

### 1. stockanalysis.com ✅（推荐）
- 网址：`https://stockanalysis.com/stocks/{symbol}/`
- 内容：PE、EPS、Forward PE、52W高低、市值、分析师评级等
- 浏览器打开即可抓取
- **无反爬，简单可靠**

### 2. Alpaca CLI
- 安装：`go install github.com/alpacahq/cli/cmd/alpaca@latest`
- 配置：`alpaca profile login --api-key --key XXXXXX --secret XXXXXX --paper --name zhima`
- 用途：下单、查持仓、实时报价（有限）
- **注意：VIX不可交易数据，市场数据覆盖不全**

### 3. Yahoo Finance
- API：`https://query1.finance.yahoo.com/v7/finance/quote?symbols=XXX`
- 状态：❌ 从腾讯云VM访问被限流（Edge: Too Many Requests）
- 可以用浏览器访问

## 不可用的数据源

### Yahoo Finance API
- 从腾讯云VM直接调用会被限流
- 解决：改用浏览器访问 stockanalysis.com

### Google搜索
- 被机器人检测拦截
- 解决：不使用

### Finnhub API
- API Key无效或权限不足
- 解决：使用其他数据源

## yfinance Python API（2024+新版本）

⚠️ **重要变更**：yfinance 2024年后返回多层索引DataFrame，列结构为`(Price类型, Ticker)`，需要额外处理才能得到干净的(ticker × date)格式。

```python
import yfinance as yf

# ❌ 旧方式（2024年前）
# closes = yf.download(UNIVERSE, period="4y")['Adj Close']  # KeyError

# ✅ 新方式（2024年后）
data = yf.download(UNIVERSE, period="4y", progress=False, auto_adjust=False)
# 1. 交换列层级：(Price, Ticker) → (Ticker, Price)
data.columns = data.columns.swaplevel(0, 1)
# 2. 按Ticker排序
data = data.sort_index(axis=1, level=0)
# 3. 提取收盘价（现在Ticker是外层）
closes = data.xs('Close', axis=1, level=1)
closes = closes.fillna(method='ffill')
# 结果: DataFrame shape = (日期, 股票代码)
```

**auto_adjust参数**：
- `auto_adjust=False`：返回多层列，包含 `Close`、`Adj Close`、`High` 等
- `auto_adjust=True`：自动调整，只返回调整后价格（单层列，但只有一列价格）

## 芝麻扫描流程

```bash
# 1. 浏览器访问 stockanalysis.com 获取数据
# NVDA: https://stockanalysis.com/stocks/nvda/
# MSFT: https://stockanalysis.com/stocks/msft/
# META: https://stockanalysis.com/stocks/meta/
# PLTR: https://stockanalysis.com/stocks/pltr/
# CRWD: https://stockanalysis.com/stocks/crwd/

# 2. 使用Alpaca CLI查实时价格（有限）
export PATH=$PATH:/root/go/bin
alpaca data latest-quote --symbol NVDA --profile zhima

# 3. 获取VIX（通过VIXY/UVXY/VXX ETF）
export PATH=$PATH:/root/go/bin
alpaca data latest-quote --symbol VIXY --profile zhima
alpaca data latest-quote --symbol UVXY --profile zhima
```

## VIX替代方案（已验证可用）⚠️

由于VIX本身不能直接交易，且很多API无法访问，可用以下**ETF替代**：

| ETF | 说明 | 特点 |
|-----|------|------|
| VIXY | 标准VIX短期期货ETF | 最接近真实VIX |
| UVXY | 2倍杠杆VIX | 波动更大，适合激进操作 |
| VXX | iPath VIX短期期货ETF | 流动性好 |

**Alpaca CLI查询方法：**
```bash
export PATH=$PATH:/root/go/bin
alpaca data latest-quote --symbol VIXY --profile zhima
alpaca data latest-quote --symbol UVXY --profile zhima
alpaca data latest-quote --symbol VXX --profile zhima
```

**芝麻策略应用：**
- VIX > 30（对应VIXY > 30 或 UVXY > 39）：市场极度恐惧 → 逆向买入 💰
- VIX < 15（对应VIXY < 15 或 VIXY < 20）：市场极度贪婪 → 分批止盈

> ⚠️ 注意：UVXY是2倍杠杆，波动是VIXY的2倍。保守策略用VIXY，激进策略可用UVXY。

## 关键指标解读

| 指标 | 芝麻v4.0标准 |
|------|------------|
| PE(TTM) | ≤20 优秀，20-30 合理，>30 回避 |
| Forward PE | 未来预期PE，越低越好 |
| EPS增长 | ≥15% 符合双击条件 |
| PEG | <1 强烈买入，<1.3 买入 |
| 52W区间 | 接近低点=安全边际高 |
