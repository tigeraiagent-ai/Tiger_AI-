#!/usr/bin/env python3
"""
x_hunter.py v3.1 - 基于官方 syndication.twitter.com 的完整推文抓取
用subprocess+curl绕过Python requests的rate limit问题
"""
import subprocess, re, json, time, html, shlex
from datetime import datetime

ENDPOINT = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}?limit=50"

TRACKED_ACCOUNTS = [
    {"username": "aleabitoreddit", "name": "Serenity", "tags": ["AI/半导体", "窭口", "轧空"]},
    {"username": "MarioNawfal", "name": "Mario Nawfal", "tags": ["M&A/AI", "并购", "全球宏观"]},
]

SKIP_SYMBOLS = {
    'AAPL','NVDA','AMD','TSLA','META','MSFT','AMZN','GOOGL','AVGO','INTC',
    'ASML','TSM','TQQQ','QQQ','SPY','DIA','IWM','GLD','SLV','UVXY',
    'PLTR','COIN','MSTR','HOOD','IBKR','RIVN','LCID','NIO','XPEV','PDD','BABA'
}

def detect_sentiment(text, symbol):
    t = text.lower()
    if re.search(r'short interest is|short interest (was|were|being)?', t):
        return "LONG_SI", 3
    if re.search(r'shorts (are|were|getting|will be|pound|cover|squeezed)', t):
        return "LONG_SQ", 3
    if 'underwater' in t and 'short' in t:
        return "LONG_SQ", 2
    if re.search(r'cut\s+(some|my)?\s*exposure', t):
        return "BEARISH_CUT", 2
    if re.search(r'rotated (it|out|to)', t):
        return "BEARISH_CUT", 2
    if re.search(r'reduced|trimmed|sold out|exited', t):
        return "BEARISH_CUT", 2
    if re.search(r'(went long|added|accumulated|loading|in at|buy|laying out)', t):
        return "LONG", 2
    if re.search(r'(warn|red flag|overvalued|bubble|avoid|danger)', t):
        return "BEARISH", 2
    b = sum(1 for k in ['bullish','long','buy','added','accumulate','upside','breakout',
                          'squeeze','short covering','moonshot','deep value','undervalued',
                          'opportunity','insane entry','dip buy'] if k in t)
    a = sum(1 for k in ['bearish','short','sell','put','warn','risk','avoid',
                          'drop','cut','reduce','sold','exited','overvalued'] if k in t)
    if b > a:
        return "LONG", b
    elif a > b:
        return "BEARISH", a
    elif 'long ' in t:
        return "LONG_KEYWORD", 1
    elif re.search(r'\$?\bshort\b', t):
        return "BEARISH_KEYWORD", 1
    return "NEUTRAL", 0

def fetch_via_curl(url):
    cmd = ['curl', '-s', '--max-time', '20',
           '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
           '-H', 'Referer: https://syndication.twitter.com/',
           url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if r.returncode != 0:
        return None
    return r.stdout

def extract_tweets(raw_text):
    tweets = []
    pattern = r'"full_text"\s*:\s*"((?:[^"\\]|\\.)*)"'
    for m in re.finditer(pattern, raw_text):
        text = m.group(1)
        text = text.encode().decode('unicode_escape')
        text = html.unescape(text)
        tweets.append(text)
    return tweets

def extract_signals(tweet_text):
    results = []
    for m in re.finditer(r'\$([A-Z]{1,5})\b', tweet_text):
        sym = m.group(1)
        if sym in SKIP_SYMBOLS:
            continue
        if sym == 'FN' and ('AAOI' in tweet_text or 'INTC' in tweet_text):
            continue
        idx = m.start()
        context = tweet_text[max(0,idx-200):min(len(tweet_text),idx+200)]
        sentiment, strength = detect_sentiment(context, sym)
        results.append({'symbol': sym, 'sentiment': sentiment, 'strength': strength, 'context': context})
    return results

def main():
    print(f"[{datetime.now().strftime('%H:%M')}] === X博主语义狩猎(v3.1) ===")
    all_long, all_bear = [], []

    for acct in TRACKED_ACCOUNTS:
        url = ENDPOINT.format(username=acct['username'])
        raw = fetch_via_curl(url)
        if raw is None:
            print(f"  抓取失败")
            continue
        tweets = extract_tweets(raw)
        print(f"  {acct['username']}: {len(tweets)}条推文")

        signals = {}
        for tweet in tweets:
            for s in extract_signals(tweet):
                key = (s['symbol'], s['sentiment'])
                if key not in signals or s['strength'] > signals[key]['strength']:
                    signals[key] = s

        all_sigs = list(signals.values())
        LONG_TYPES = {'LONG','LONG_SI','LONG_SQ','LONG_KEYWORD','LONG_BENEFIT'}
        BEARISH_TYPES = {'BEARISH','BEARISH_CUT','BEARISH_KEYWORD'}
        long_sigs = [s for s in all_sigs if s['sentiment'] in LONG_TYPES]
        bear_sigs  = [s for s in all_sigs if s['sentiment'] in BEARISH_TYPES]

        print(f"  看多:{len(long_sigs)} | 看空:{len(bear_sigs)}")
        for s in long_sigs:
            ctx = s['context'][:80].replace('\n',' ')
            print(f"    🟢 ${s['symbol']} [{s['sentiment']}] {ctx}...")
        for s in bear_sigs:
            ctx = s['context'][:80].replace('\n',' ')
            print(f"    🔴 ${s['symbol']} [{s['sentiment']}] {ctx}...")

        all_long.extend(long_sigs)
        all_bear.extend(bear_sigs)

    out = "/root/venv_zhima/data/opportunity_hunting/x_signals.json"
    with open(out, 'w') as f:
        json.dump({'long': all_long, 'bearish': all_bear}, f, indent=2, default=str)
    print(f"\n  总计: 🟢{len(all_long)} 🔴{len(all_bear)}")
    return all_long, all_bear

if __name__ == "__main__":
    main()