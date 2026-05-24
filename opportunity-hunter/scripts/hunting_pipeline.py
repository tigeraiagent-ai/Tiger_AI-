#!/usr/bin/env python3
"""
芝麻主动狩猎整合脚本 - 跑完整流水线
X博主抓取 → 语义分析 → 候选池更新 → 精选交易信号生成 → 报告 → 推送
"""
import sys, os
sys.path.insert(0, "/root/venv_zhima/scripts")

from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M')}] {msg}")

def main():
    log("=== 芝麻主动狩猎流水线启动 ===")

    # Step 1: X博主抓取+语义分析
    log("Step 1: X博主语义狩猎...")
    import x_hunter
    long_sigs, bear_sigs = x_hunter.main()

    # Step 2: 更新候选池 + 精选交易信号
    log("Step 2: 更新候选池+生成精选交易信号...")
    from opportunity_hunting import add_candidate
    from hunting_signals import add_hunting_signal, get_pending_signals

    pending = {s['symbol'] for s in get_pending_signals()}

    # 强信号：LONG_SI/LONG_SQ（轧空逻辑）
    strong_sigs = [s for s in long_sigs if s['sentiment'] in ('LONG_SI', 'LONG_SQ')]
    # 中强信号：LONG + 强逻辑关键词
    medium_sigs = [s for s in long_sigs if s['sentiment'] == 'LONG' and s['strength'] >= 2]

    trade_signals = []

    for s in strong_sigs:
        reason = s['context'][:80].replace('\n', ' ')
        add_candidate('CHOKEPOINT', s['symbol'],
                     f"X博主Serenity [{s['sentiment']}] {reason}", 'x_hunter')
        if s['symbol'] not in pending:
            add_hunting_signal(s['symbol'], 'BUY', reason, s['sentiment'],
                              stop_loss=0.90, target=1.40, position_pct=0.05)
            trade_signals.append(s)

    for s in medium_sigs:
        reason = s['context'][:80].replace('\n', ' ')
        add_candidate('CHOKEPOINT', s['symbol'],
                     f"X博主Serenity [{s['sentiment']}] {reason}", 'x_hunter')
        if s['symbol'] not in pending:
            add_hunting_signal(s['symbol'], 'BUY', reason, s['sentiment'],
                              stop_loss=0.92, target=1.25, position_pct=0.03)
            trade_signals.append(s)

    log(f"  看多信号: {len(long_sigs)} | 交易信号: {len(trade_signals)}")

    # Step 3: 生成报告
    log("Step 3: 生成狩猎报告...")
    from opportunity_hunting import report as gen_report
    gen_report()

    log("=== 流水线完成 ===")
    if trade_signals:
        for s in trade_signals:
            log(f"  → ${s['symbol']} [{s['sentiment']}] {s['context'][:60].replace(chr(10),' ')}...")

if __name__ == "__main__":
    main()