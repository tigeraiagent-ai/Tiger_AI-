#!/usr/bin/env python3
"""
financial_analyzer.py - 芝麻财务分析模块
仿Dexter get_financials + key_ratios 设计
数据源: yfinance (免费)

候选股深度分析 → 窭口机会验证
"""
import yfinance as yf
import json
from datetime import datetime
from typing import Optional

CACHE_DIR = "/root/venv_zhima/data/financial_cache"

def _cache_path(ticker: str) -> str:
    import os
    os.makedirs(CACHE_DIR, exist_ok=True)
    return f"{CACHE_DIR}/{ticker}.json"

def _get_cached(ticker: str, ttl: int = 3600) -> Optional[dict]:
    import os, time
    p = _cache_path(ticker)
    if not os.path.exists(p):
        return None
    if time.time() - os.path.getmtime(p) > ttl:
        return None
    with open(p) as f:
        return json.load(f)

def _set_cached(ticker: str, data: dict):
    with open(_cache_path(ticker), 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_company_info(ticker: str) -> dict:
    cached = _get_cached(f"{ticker}_info", 86400)
    if cached:
        return cached
    try:
        t = yf.Ticker(ticker)
        info = t.info
        data = {
            "ticker": ticker,
            "companyName": info.get("longName", info.get("shortName", "")),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "marketCap": info.get("marketCap", 0),
            "employees": info.get("fullTimeEmployees", 0),
            "exchange": info.get("exchange", ""),
            "website": info.get("website", ""),
        }
        _set_cached(f"{ticker}_info", data)
        return data
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

def get_key_ratios(ticker: str) -> dict:
    """关键财务指标（仿Dexter get_key_ratios）"""
    cached = _get_cached(f"{ticker}_ratios")
    if cached:
        return cached
    try:
        t = yf.Ticker(ticker)
        info = t.info
        income = t.income_stmt
        balance = t.balance_sheet

        # ROE计算（找正确的行）
        net_income, stockholders_equity = None, None
        if income is not None and not income.empty:
            for idx in income.index:
                s = str(idx)
                if 'Net Income' in s and 'Noncontrolling' not in s and 'Minority' not in s:
                    net_income = float(income.loc[idx, income.columns[0]])
                    break
        if balance is not None and not balance.empty:
            for idx in balance.index:
                if 'Stockholders Equity' in str(idx):
                    stockholders_equity = float(balance.loc[idx, balance.columns[0]])
                    break

        roe = round(net_income / stockholders_equity, 4) if (net_income and stockholders_equity) else None

        # 清理Timestamp字段
        def clean(v):
            if v is None: return None
            if isinstance(v, (int, float, bool)): return v
            return str(v)

        data = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "valuation": {
                "peRatio": clean(info.get("trailingPE")),
                "forwardPe": clean(info.get("forwardPE")),
                "pegRatio": clean(info.get("pegRatio")),
                "priceToBook": clean(info.get("priceToBook")),
                "marketCap": clean(info.get("marketCap")),
                "evToEbitda": clean(info.get("enterpriseToEbitda")),
            },
            "profitability": {
                "grossMargin": clean(info.get("grossMargins")),
                "operatingMargin": clean(info.get("operatingMargins")),
                "netMargin": clean(info.get("profitMargins")),
                "roe": roe,
                "roa": clean(info.get("returnOnAssets")),
            },
            "perShare": {
                "eps": clean(info.get("trailingEps")),
                "forwardEps": clean(info.get("forwardEps")),
                "bookValue": clean(info.get("bookValue")),
            },
            "dividends": {
                "dividendYield": clean(info.get("dividendYield")),
                "dividendRate": clean(info.get("dividendRate")),
            },
            "growth": {
                "revenueGrowth": clean(info.get("revenueGrowth")),
                "earningsGrowth": clean(info.get("earningsGrowth")),
            },
            "leverage": {
                "debtToEquity": clean(info.get("debtToEquity")),
                "currentRatio": clean(info.get("currentRatio")),
            },
            "analyst": {
                "targetPrice": clean(info.get("targetMeanPrice")),
                "recommendation": info.get("recommendationKey"),
            },
        }
        _set_cached(f"{ticker}_ratios", data)
        return data
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "trace": ""}

def get_income_statements(ticker: str, limit: int = 4) -> dict:
    """损益表"""
    try:
        t = yf.Ticker(ticker)
        income = t.income_stmt
        if income is None or income.empty:
            return {"ticker": ticker, "error": "No income data"}
        cols = list(income.columns[:limit])
        rows = {}
        for row_name in ["Total Revenue", "Gross Profit", "Operating Income",
                         "Net Income From Continuing Operation Net Minority Interest",
                         "EBITDA", "EPS"]:
            matches = [r for r in income.index if row_name in str(r)]
            if matches:
                vals = []
                for col in cols:
                    try:
                        vals.append(float(income.loc[matches[0], col]))
                    except:
                        vals.append(None)
                rows[row_name] = vals
        return {"ticker": ticker, "periods": [str(c)[:10] for c in cols], "rows": rows}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

def get_cashflow(ticker: str, limit: int = 4) -> dict:
    """现金流量表"""
    try:
        t = yf.Ticker(ticker)
        cf = t.cashflow
        if cf is None or cf.empty:
            return {"ticker": ticker, "error": "No cashflow data"}
        cols = list(cf.columns[:limit])
        rows = {}
        for row_name in ["Operating Cash Flow", "Free Cash Flow", "Capital Expenditure"]:
            matches = [r for r in cf.index if row_name in str(r)]
            if matches:
                vals = []
                for col in cols:
                    try:
                        vals.append(float(cf.loc[matches[0], col]))
                    except:
                        vals.append(None)
                rows[row_name] = vals
        return {"ticker": ticker, "periods": [str(c)[:10] for c in cols], "rows": rows}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

def analyze_opportunity(ticker: str) -> dict:
    """单股票完整分析（用于窭口候选股验证）"""
    info = get_company_info(ticker)
    ratios = get_key_ratios(ticker)
    income = get_income_statements(ticker)
    cashflow = get_cashflow(ticker)
    return {"timestamp": datetime.now().isoformat(), "ticker": ticker,
            "info": info, "ratios": ratios, "income": income, "cashflow": cashflow}

def screen_stocks(criteria: dict) -> list:
    """
    按财务条件筛选（仿Dexter stock_screener）
    criteria: {minMarketCap, maxPe, minGrowth, minMargin, sector}
    """
    from scripts.opportunity_hunting import load_candidates
    cands = load_candidates()
    pool = [s["symbol"] for s in cands.get("choke_point", [])]

    results = []
    for ticker in pool[:20]:
        try:
            ratios = get_key_ratios(ticker)
            if "error" in ratios:
                continue
            info = get_company_info(ticker)
            val = ratios.get("valuation", {})
            prof = ratios.get("profitability", {})
            growth = ratios.get("growth", {})

            if criteria.get("minMarketCap") and (val.get("marketCap") or 0) < criteria["minMarketCap"]:
                continue
            if criteria.get("maxPe") and val.get("peRatio") and val["peRatio"] > criteria["maxPe"]:
                continue
            if criteria.get("minGrowth") and growth.get("revenueGrowth") and growth["revenueGrowth"] < criteria["minGrowth"]:
                continue
            if criteria.get("minMargin") and prof.get("netMargin") and prof["netMargin"] < criteria["minMargin"]:
                continue

            results.append({
                "ticker": ticker,
                "marketCap": val.get("marketCap"),
                "peRatio": val.get("peRatio"),
                "revenueGrowth": growth.get("revenueGrowth"),
                "netMargin": prof.get("netMargin"),
                "roe": prof.get("roe"),
            })
        except:
            continue
    return results

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    result = analyze_opportunity(ticker)
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False)[:3000])