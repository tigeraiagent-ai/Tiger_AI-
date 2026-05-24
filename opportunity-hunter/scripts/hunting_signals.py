#!/usr/bin/env python3
"""
hunting_signals.json - 狩猎引擎生成的交易信号
由hunting_pipeline.py写入，由auto_trade_executor.py读取执行

结构：
{
  "signals": [
    {
      "symbol": "AEVA",
      "action": "BUY",           # BUY / SELL
      "entry_price": null,       # null = 市价入场
      "stop_loss": 0.92,         # 止损价（相对入场价的比例）
      "target": 1.25,            # 目标价（相对入场价的比例）
      "quantity": null,         # null = 自动计算仓位
      "position_pct": 0.10,     # 账户资金使用比例（10%）
      "signal_type": "LONG_SQ", # 信号来源
      "source": "x_hunter",      # 来源
      "reason": "shorts underwater轧空+US institutions接入",
      "created": "2026-05-23T19:44:00",
      "status": "PENDING",      # PENDING / FILLED / EXPIRED / CANCELLED
      "filled_at": null,
      "filled_price": null,
      "expired_at": null         # 信号过期时间（默认24小时后）
    }
  ]
}
"""
import json, os
from datetime import datetime, timedelta
from typing import Optional

SIGNAL_FILE = "/root/venv_zhima/data/hunting_signals.json"

def load_signals() -> dict:
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE) as f:
            return json.load(f)
    return {"signals": [], "last_updated": datetime.now().isoformat()}

def save_signals(data: dict):
    data["last_updated"] = datetime.now().isoformat()
    with open(SIGNAL_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def add_hunting_signal(symbol: str, action: str, reason: str,
                       signal_type: str = "CHOKEPOINT",
                       entry_price: float = None,
                       stop_loss: float = 0.92,
                       target: float = 1.25,
                       position_pct: float = 0.10,
                       quantity: int = None,
                       ttl_hours: int = 24):
    """
    添加一个狩猎交易信号
    """
    data = load_signals()

    # 检查是否已有未执行的同标的信号
    for s in data["signals"]:
        if s["symbol"] == symbol and s["status"] == "PENDING":
            # 更新信号
            s["reason"] = reason
            s["signal_type"] = signal_type
            s["created"] = datetime.now().isoformat()
            s["action"] = action
            save_signals(data)
            return s

    sig = {
        "symbol": symbol.upper(),
        "action": action.upper(),
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target": target,
        "position_pct": position_pct,
        "quantity": quantity,
        "signal_type": signal_type,
        "source": "hunting_pipeline",
        "reason": reason,
        "created": datetime.now().isoformat(),
        "status": "PENDING",
        "filled_at": None,
        "filled_price": None,
        "expired_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
    }
    data["signals"].append(sig)
    save_signals(data)
    return sig

def mark_filled(symbol: str, filled_price: float):
    """标记信号已成交"""
    data = load_signals()
    for s in data["signals"]:
        if s["symbol"] == symbol and s["status"] == "PENDING":
            s["status"] = "FILLED"
            s["filled_at"] = datetime.now().isoformat()
            s["filled_price"] = filled_price
            save_signals(data)
            return True
    return False

def cancel_signal(symbol: str):
    """取消信号"""
    data = load_signals()
    for s in data["signals"]:
        if s["symbol"] == symbol and s["status"] == "PENDING":
            s["status"] = "CANCELLED"
            save_signals(data)
            return True
    return False

def get_pending_signals():
    """获取所有待执行信号"""
    data = load_signals()
    now = datetime.now()
    pending = []
    for s in data["signals"]:
        if s["status"] != "PENDING":
            continue
        # 检查是否过期
        if s.get("expired_at"):
            expiry = datetime.fromisoformat(s["expired_at"].replace("Z", "+00:00"))
            if now > expiry:
                s["status"] = "EXPIRED"
                continue
        pending.append(s)
    save_signals(data)
    return pending

def clear_filled():
    """清理已成交信号（只保留最近10条）"""
    data = load_signals()
    filled = [s for s in data["signals"] if s["status"] == "FILLED"]
    others = [s for s in data["signals"] if s["status"] != "FILLED"]
    data["signals"] = others + filled[-10:]
    save_signals(data)

if __name__ == "__main__":
    # 测试
    add_hunting_signal("AEVA", "BUY", "shorts underwater轧空+US institutions接入", "LONG_SQ")
    add_hunting_signal("SPRB", "BUY", "目标价$500，罕见病ERT特攻", "LONG", stop_loss=0.85, target=2.0)
    print("当前待执行信号:")
    for s in get_pending_signals():
        print(f"  {s['symbol']} {s['action']} | SL={s['stop_loss']} T={s['target']} | {s['reason'][:50]}")