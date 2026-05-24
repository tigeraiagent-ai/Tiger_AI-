#!/usr/bin/env python3
"""
芝麻主动机会狩猎引擎 v1.0
每交易时段自动运行，主动发现机会而非被动等待信号
"""
import os, json, time
from datetime import datetime

DATA_DIR   = "/root/venv_zhima/data/opportunity_hunting"
QUEUE_DIR = "/root/venv_zhima/data"

OPPORTUNITY_TYPES = {
    "CHOKEPOINT":   "窭口概念（X博主+产业逻辑）",
    "SHORTSQUEEZE":"轧空机会（SI%+量价）",
    "DAVIS_DOUBLE":"Davis双击（业绩+动量）",
    "SOS_BREAKOUT":"SOS突破（技术形态）",
    "INDEX_FLOW":  "指数资金（MSCI/NASDAQ纳入）",
    "ANIMAL_MOOD": "动物情绪（WSB热度+SI%）",
}

SIGNALS_FILE  = f"{DATA_DIR}/opportunity_signals.json"
CANDIDATES_FILE = f"{DATA_DIR}/hunting_candidates.json"
REPORT_FILE  = f"{DATA_DIR}/hunting_report.txt"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def load_candidates():
    """加载候选股票池"""
    f = CANDIDATES_FILE
    if os.path.exists(f):
        with open(f) as fp:
            return json.load(fp)
    return {
        "choke_point": [],   # 窭口概念股（来自X博主）
        "squeeze":     [],   # 轧空候选（SI%>25%）
        "davis":        [],   # Davis双击候选
        "sos":          [],   # SOS形态候选
        "index_flow":   [],   # 指数纳入候选
        "animal":       [],   # 动物股候选
    }

def save_candidates(candidates):
    with open(CANDIDATES_FILE, 'w') as f:
        json.dump(candidates, f, indent=2)

def add_candidate(op_type, sym, reason, source="system"):
    """添加候选股票"""
    candidates = load_candidates()
    key_map = {
        "CHOKEPOINT":   "choke_point",
        "SHORTSQUEEZE": "squeeze",
        "DAVIS_DOUBLE": "davis",
        "SOS_BREAKOUT": "sos",
        "INDEX_FLOW":  "index_flow",
        "ANIMAL_MOOD": "animal",
    }
    key = key_map.get(op_type, op_type.lower())
    if key not in candidates:
        candidates[key] = []
    
    # 检查是否已存在
    for c in candidates[key]:
        if c['symbol'] == sym:
            c['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            c['reason'] = reason
            c['source'] = source
            break
    else:
        candidates[key].append({
            'symbol':   sym,
            'reason':   reason,
            'source':   source,
            'added':    datetime.now().strftime("%Y-%m-%d %H:%M"),
            'updated':  datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    
    # 保留最近20只
    candidates[key] = candidates[key][-20:]
    save_candidates(candidates)

def report():
    """生成每日主动狩猎报告"""
    candidates = load_candidates()
    now = datetime.now().strftime("%Y-%m-%d %H:%M ET")
    
    lines = [f"🎯 芝麻主动狩猎报告 [{now}]", "="*50, ""]
    
    total = sum(len(v) for v in candidates.values())
    lines.append(f"候选股票总数: {total} 只")
    lines.append(f"  窭口概念: {len(candidates.get('choke_point',[]))} 只")
    lines.append(f"  轧空机会: {len(candidates.get('squeeze',[]))} 只")
    lines.append(f"  Davis双击: {len(candidates.get('davis',[]))} 只")
    lines.append(f"  SOS突破: {len(candidates.get('sos',[]))} 只")
    lines.append(f"  指数资金: {len(candidates.get('index_flow',[]))} 只")
    lines.append(f"  动物情绪: {len(candidates.get('animal',[]))} 只")
    lines.append("")
    
    for op_type, name in OPPORTUNITY_TYPES.items():
        key_map = {
            "CHOKEPOINT":   "choke_point",
            "SHORTSQUEEZE": "squeeze",
            "DAVIS_DOUBLE": "davis",
            "SOS_BREAKOUT": "sos",
            "INDEX_FLOW":  "index_flow",
            "ANIMAL_MOOD": "animal",
        }
        key = key_map[op_type]
        stocks = candidates.get(key, [])
        if stocks:
            lines.append(f"📌 {name}:")
            for s in stocks[-5:]:  # 只显示最近5只
                lines.append(f"  • {s['symbol']} | {s['reason'][:40]} | 来源:{s['source']}")
            lines.append("")
    
    report = "\n".join(lines)
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    
    # 写入队列推送给虎哥（非交易时段发，交易时段走自动扫描）
    queue_file = f"{QUEUE_DIR}/opportunity_hunting_queue.txt"
    with open(queue_file, 'w') as f:
        f.write(report)
    
    log(f"狩猎报告已生成: {total} 只候选")
    return report

def main():
    log("=== 芝麻主动狩猎引擎启动 ===")
    candidates = load_candidates()
    total = sum(len(v) for v in candidates.values())
    log(f"当前候选池: {total} 只")
    report()

if __name__ == "__main__":
    main()