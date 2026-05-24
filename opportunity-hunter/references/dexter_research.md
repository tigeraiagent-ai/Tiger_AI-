# Dexter 架构研究报告

**来源**: https://github.com/virattt/dexter
**研究时间**: 2026-05-23
**内化部分**: 推理日志 + 工具限流

---

## 核心架构

```
Dexter Agent Loop:
  1. 微压缩(microcompact) - 每轮轻量级修剪
  2. LLM流式调用 - chunk累积+AIMessage
  3. 工具并发执行 - concurrencyMap控制
  4. 上下文阈值管理 - 超阈值触发压缩
  5. Scratchpad日志 - 每步记录推理链
```

---

## Scratchpad 推理日志

**文件格式**: JSONL（追加写入，防崩溃）
**存储位置**: `.dexter/scratchpad/时间戳_hash.jsonl`

**记录类型**:
```json
{"type": "init", "content": "查询", "timestamp": "..."}
{"type": "thinking", "content": "推理步骤", "timestamp": "..."}
{"type": "tool_result", "tool": "get_financials", "args": {...}, "result_summary": "...", "timestamp": "..."}
{"type": "decision", "action": "买入", "reason": "...", "confidence": 0.87, "timestamp": "..."}
```

**芝麻实现**: `reasoning_log.py` → `/root/venv_zhima/data/scratchpad/`

---

## 工具限流软限制

**机制**: 警告但不阻止（防止扼杀探索）
**默认**: 每工具最多3次调用

```typescript
canCallTool(toolName): { allowed: boolean; warning?: string }
// 0-2次: 正常
// 2次: "快到建议上限"
// 3次+: "已超建议上限，考虑换工具"
```

---

## 上下文压缩

**两层压缩**:
1. **Microcompact**（每轮）: 移除旧tool_result中的冗余字段
2. **Full Compaction**（阈值触发）: 大结果写磁盘→注入预览+文件路径

芝麻当前差距:
- SOS扫描无压缩 → 候选股多时可能溢出
- 无大结果外存机制

---

## 财务工具链

| 工具 | Dexter数据源 | 芝麻现状 |
|------|------------|---------|
| get_financials | Financial Datasets API | yfinance（数据不完整） |
| read_filings | SEC EDGAR | 无 |
| stock_screener | Financial Datasets筛选器 | 手动SI%硬编码 |
| get_market_data | yfinance/stocknews | yfinance |

**Financial Datasets API**: $49/月，机构级财报数据

---

## 内化清单

- [x] 推理日志 (reasoning_log.py)
- [ ] 工具限流警告（嵌入脚本）
- [ ] 财务数据库（Financial Datasets API）— 需虎哥授权费用
- [ ] SEC文件读取 — 无API，需EDGAR直接爬
- [ ] 搜索降级链（当前只有Google News单渠道）

---

## 待做事项

1. **财务数据升级**: Financial Datasets API（$49/月）
   - 可获取: 10-K/10-Q/8-K/13F完整数据
   - 当前yfinance只有价格+基本指标

2. **SOS扫描升级**: 加入Dexter式推理日志
   - 每次扫描完整记录
   - AlphaEvo进化可回溯

3. **搜索降级链**:
   - 当前: Google News
   - 目标: NewsAPI → DuckDuckGo → Tavily