# 芝麻主动狩猎引擎 - 参考文档

## X博主语义分析模块

### 支持的博主
- @aleabitoreddit (Serenity) - AI/半导体供应链窭口分析师

### 语义判断规则

#### 🟢 看多信号
| 规则 | 语境示例 | 信号类型 |
|------|---------|---------|
| 高做空比例 | "short interest is high" | LONG_SI |
| 空头被套 | "shorts are underwater" | LONG_SQ |
| 窭口垄断 | "monopoly over SOI" | LONG |
| 她加仓 | "I went long" / "added" | LONG |
| 机构买散户卖 | "institutions buying, retail sold" | LONG_BENEFIT |

#### 🔴 看空信号
| 规则 | 语境示例 | 信号类型 |
|------|---------|---------|
| 她减仓 | "I cut some exposure" | BEARISH_CUT |
| 换仓离开 | "rotated it to CPO names" | BEARISH_CUT |
| 警示风险 | "red flag" / "warn" / "avoid" | BEARISH |

#### ⚠️ 误判防护
- "short" 在 "short interest" 中不是做空信号
- "long sushi" = 特朗普吃寿司，不是股票
- FN 是 AAOI 附近的误关联，已过滤

### 窭口产业链层级

```
第一层（已定价）: GPU / HBM / 网络 / 数据中心
第二层（窭口）: 光模块 / 激先器 / InP衬底 / SOI晶圆
第三层（隐形金矿）: 外延设备 / 晶圆测试 / IC载板 / 特殊铜纤
```

### Serenity 历史战绩

| 股票 | 涨幅 | 逻辑 |
|------|------|------|
| AXTI | +1000% | InP衬底窭口 |
| SIVE | +73% | CPO供应链+指数纳入 |
| Soitec (SOI) | +16%~40% | SOI晶圆垄断 |
| RPI | +90% | FTSE250纳入 |
| SPCB | +50%+ | WSB动物股 |

### 候选股票池现状（2026-05-23）

```
窭口概念: SIVE/SOI/AXTI/TSEM/FOCI/RPI/SMCI/AEVA/JBL/POET/MRVL等
轧空机会: SLS/MRNO/NVAX/PCT/BTDR/WRLD/WEN/FORR
看空警示: LITE/COHR/BOT/SMTOY/KOPN/DGXX
```