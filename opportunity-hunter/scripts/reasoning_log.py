#!/usr/bin/env python3
"""
芝麻推理日志 - Dexter Scratchpad风格
每次扫描生成JSONL日志，记录完整推理链
用于AlphaEvo进化回溯和问题诊断
"""
import json, os
from datetime import datetime
from pathlib import Path
from hashlib import md5

SCRATCHPAD_DIR = "/root/venv_zhima/data/scratchpad"

def _ensure_dir():
    os.makedirs(SCRATCHPAD_DIR, exist_ok=True)

def _mk_filename(tag: str) -> str:
    h = md5(tag.encode()).hexdigest()[:12]
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S").replace(":", "")
    return f"{ts}_{h}.jsonl"

class ReasoningLog:
    """
    仿Dexter Scratchpad的推理日志
    每条记录: {"type": "init"|"thinking"|"tool_result", "timestamp", ...}
    """
    def __init__(self, query: str, tag: str = "sos"):
        _ensure_dir()
        self.query = query
        self.filepath = os.path.join(SCRATCHPAD_DIR, _mk_filename(tag))
        self._entries = []
        self._tool_counts = {}
        # 写入init
        self._write({
            "type": "init",
            "content": query,
            "timestamp": datetime.now().isoformat(),
        })

    def add_thinking(self, message: str):
        """记录推理思考"""
        self._write({
            "type": "thinking",
            "content": message,
            "timestamp": datetime.now().isoformat(),
        })

    def add_tool_start(self, tool: str, args: dict):
        """工具开始调用"""
        self._write({
            "type": "tool_start",
            "tool": tool,
            "args": args,
            "timestamp": datetime.now().isoformat(),
        })

    def add_tool_result(self, tool: str, args: dict, result: str, summary: str = ""):
        """工具返回结果"""
        # 计数
        self._tool_counts[tool] = self._tool_counts.get(tool, 0) + 1
        self._write({
            "type": "tool_result",
            "tool": tool,
            "args": args,
            "result_summary": summary or result[:200],
            "full_result_file": None,  # 大结果可写磁盘
            "timestamp": datetime.now().isoformat(),
        })

    def add_decision(self, action: str, reason: str, confidence: float):
        """记录最终决策"""
        self._write({
            "type": "decision",
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        })

    def tool_warning(self, tool: str) -> str | None:
        """仿Dexter软限制警告"""
        count = self._tool_counts.get(tool, 0)
        if count >= 3:
            return (f"⚠️ '{tool}' 已调用{count}次(建议≤3次)。"
                    f"如结果不够，考虑换工具或用现有数据做决策。")
        if count == 2:
            return f"⚠️ '{tool}' 已调用{count}次，快到建议上限。"
        return None

    def format_summary(self) -> str:
        """生成人类可读的推理摘要"""
        lines = [f"[推理日志] {self.filepath}", f"查询: {self.query}"]
        for e in self._entries:
            if e["type"] == "thinking":
                lines.append(f"  🤔 {e['content'][:100]}")
            elif e["type"] == "decision":
                lines.append(f"  → {e['action']} (置信{e.get('confidence',0):.0%}): {e['reason'][:80]}")
        return "\n".join(lines)

    def _write(self, entry: dict):
        self._entries.append(entry)
        with open(self.filepath, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    # 测试
    log = ReasoningLog("SOS扫描 NVDA AMD", "test")
    log.add_thinking("开始扫描，检测到TQQQ下跌需要关注")
    log.add_tool_start("yfinance", {"ticker": "NVDA"})
    log.add_tool_result("yfinance", {"ticker": "NVDA"}, '{"price": 120.5}', "NVDA当前价格$120.50")
    log.add_decision("买入", "SOS信号确认+放量", 0.87)
    print(log.format_summary())
    print(f"\n日志文件: {log.filepath}")