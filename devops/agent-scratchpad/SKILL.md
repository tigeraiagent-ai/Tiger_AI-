---
name: agent-scratchpad
description: Agent运行日志记录技能 — 每次tool call的输入输出存档，方便复盘和调试。适用于多步骤复杂任务的调试和结果验证。
tags: [debug, logging, scratchpad, agent, devops]
last_updated: 2026-05-23
derived_from: virattt/dexter scratchpad system
---

# Agent Scratchpad 日志技能 v1.0

源自Dexter的scratchpad调试系统。每次agent任务的tool call输入输出存档，方便复盘。

## 核心价值

> *"Every model is wrong. Some are useful."*

调试日志让你知道模型**实际上**做了什么，而非你以为它做了什么。

## 工作原理

```
任务执行 → 每次Tool Call记录 → JSONL文件 → 事后复盘
```

## 文件格式

```
.dexter/scratchpad/YYYY-MM-DD-HHMMSS_queryhash.jsonl
```

每行是一个JSON对象：

```json
{"type": "tool_start", "tool": "get_financials", "input": {"query": "NVDA cash flow"}, "timestamp": "2026-05-23T19:30:00Z"}
{"type": "tool_end", "tool": "get_financials", "output": {"cash_flow": [...], "metadata": {...}}, "duration_ms": 1234}
{"type": "thinking", "content": "Cash flow looks weak, need to check revenue growth...", "timestamp": "2026-05-23T19:30:02Z"}
{"type": "answer_start", "timestamp": "2026-05-23T19:30:05Z"}
{"type": "done", "final_answer": "...", "tokens_used": 45000, "duration_s": 45}
```

## 事件类型

| type | 说明 | 用途 |
|------|------|------|
| `tool_start` | 工具调用发起 | 追踪执行顺序 |
| `tool_end` | 工具调用完成 | 验证输出 |
| `tool_error` | 工具执行失败 | 快速定位问题 |
| `thinking` | 推理过程 | 理解模型思维链 |
| `answer_start` | 开始输出最终答案 | — |
| `done` | 任务完成 | 统计资源消耗 |

## 在芝麻中的实现

### 实现方式：Python装饰器 + 文件滚动

```python
# /root/venv_zhima/scripts/scratchpad.py

import json
import os
import hashlib
from datetime import datetime
from functools import wraps
from typing import Any, Callable

SCRATCHPAD_DIR = "/root/venv_zhima/logs/scratchpad"
MAX_FILE_SIZE_MB = 5
MAX_FILES = 20

def ensure_scratchpad_dir():
    os.makedirs(SCRATCHPAD_DIR, exist_ok=True)

def rotate_old_logs():
    """只保留最近MAX_FILES个scratchpad文件"""
    files = sorted(os.listdir(SCRATCHPAD_DIR), key=lambda f: os.path.getmtime(f))
    while len(files) > MAX_FILES:
        os.remove(os.path.join(SCRATCHPAD_DIR, files.pop(0)))

def log_event(event_type: str, tool: str, data: dict, query: str = ""):
    ensure_scratchpad_dir()

    # 生成文件名
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    query_hash = hashlib.md5(query.encode()[:50]).hexdigest()[:8] if query else "noquery"
    filename = f"{ts}_{query_hash}.jsonl"

    entry = {
        "type": event_type,
        "tool": tool,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    filepath = os.path.join(SCRATCHPAD_DIR, filename)
    with open(filepath, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    rotate_old_logs()
    return filepath

def trace_tool_call(tool_name: str, query: str = ""):
    """装饰器：自动记录工具调用的输入输出"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = datetime.now()

            # 记录开始
            log_event("tool_start", tool_name, {
                "args": str(args)[:500],
                "kwargs": str(kwargs)[:500],
                "query": query
            }, query=query)

            try:
                result = func(*args, **kwargs)

                # 记录成功
                duration_ms = (datetime.now() - start).total_seconds() * 1000
                log_event("tool_end", tool_name, {
                    "duration_ms": round(duration_ms, 1),
                    "result_size": len(str(result)),
                    "result_preview": str(result)[:300]
                }, query=query)

                return result

            except Exception as e:
                # 记录错误
                duration_ms = (datetime.now() - start).total_seconds() * 1000
                log_event("tool_error", tool_name, {
                    "duration_ms": round(duration_ms, 1),
                    "error": str(e),
                    "error_type": type(e).__name__
                }, query=query)
                raise

        return wrapper
    return decorator

# ─── 便捷函数 ─────────────────────────────────────────────────

def read_scratchpad(filepath: str) -> list:
    """读取scratchpad文件，返回事件列表"""
    events = []
    with open(filepath) as f:
        for line in f:
            try:
                events.append(json.loads(line.strip()))
            except:
                continue
    return events

def get_recent_scratchpads(limit: int = 5) -> list:
    """获取最近的scratchpad文件列表"""
    ensure_scratchpad_dir()
    files = sorted(os.listdir(SCRATCHPAD_DIR), key=lambda f: os.path.getmtime(f), reverse=True)
    return [os.path.join(SCRATCHPAD_DIR, f) for f in files[:limit]]

def print_scratchpad_summary(filepath: str):
    """打印scratchpad摘要"""
    events = read_scratchpad(filepath)
    print(f"=== Scratchpad: {os.path.basename(filepath)} ===")
    print(f"总事件数: {len(events)}")
    tools_used = [e['tool'] for e in events if e['type'] in ('tool_start', 'tool_end')]
    print(f"工具调用: {len([t for t in tools_used if t == 'tool_start'])} 次")
    errors = [e for e in events if e['type'] == 'tool_error']
    if errors:
        print(f"错误: {len(errors)} 个")
        for err in errors:
            print(f"  - {err['tool']}: {err['data']['error']}")
    print()
```

## 使用示例

```python
from scripts.scratchpad import trace_tool_call, log_event, get_recent_scratchpads

@trace_tool_call("parse_news", query="TSMC news")
def parse_news(content):
    # ... 解析逻辑
    return result

@trace_tool_call("dcf_calculate", query="NVDA valuation")
def dcf_calculate(ticker):
    # ... DCF逻辑
    return result

# 调试时查看最近的任务日志
for fp in get_recent_scratchpads(3):
    print_scratchpad_summary(fp)
```

## 在cron任务中的应用

cron任务在独立session中运行，更需要scratchpad来复盘：

```python
# /root/venv_zhima/scripts/daily_scan.py

from scratchpad import log_event

def run():
    log_event("task_start", "daily_scan", {"task": "持仓扫描"})

    news = check_news()
    log_event("tool_end", "check_news", {"results": len(news)})

    signals = scan_opportunities()
    log_event("tool_end", "scan_opportunities", {"signals": signals})

    log_event("done", "daily_scan", {"signals_found": len(signals)})

if __name__ == "__main__":
    run()
```

## 日志保留策略

- 最大20个scratchpad文件（防止磁盘满）
- 单文件超5MB时停止写入（理论上不会）
- 每次写入后检查并rotate

## 文件位置

```
/root/venv_zhima/scripts/scratchpad.py     — 核心库
/root/venv_zhima/logs/scratchpad/         — scratchpad文件目录
/root/venv_zhima/logs/scratchpad/*.jsonl  — 具体日志文件
```

## 复盘流程

当某次任务结果不满意时：

1. 找到对应的scratchpad文件：`get_recent_scratchpads()` → 找到文件名
2. 读取：`read_scratchpad(filepath)` → 还原执行过程
3. 分析：`print_scratchpad_summary(fp)` → 看哪步出错
4. 修正：调整prompt/参数/工具逻辑
5. 重新跑：验证修正效果

## 重要性排序

1. **tool_error记录** — 快速定位失败原因，最重要
2. **tool_end的结果预览** — 验证输出是否符合预期
3. **tool_start的参数** — 确认调用方式是否正确
4. **thinking记录** — 理解模型推理链，仅在调试时启用（会产生大量日志）