import pandas as pd
import datetime as dt
import sqlite3
from config import DB_PATH, DAILY_REPORT_DIR, WEEKLY_REPORT_DIR

def generate_portfolio_report(market_df, portfolio):
    if market_df.empty: return None, {}

    port_df = pd.DataFrame(portfolio)
    market_df = market_df.drop(columns=["Quantity", "BuyPrice"], errors="ignore")
    merged = pd.merge(port_df, market_df, on="Ticker", how="left")

    merged["InvestedValue"] = merged["Quantity"] * merged["BuyPrice"]
    merged["CurrentValue"] = merged["Quantity"] * merged["Close"]
    merged["ProfitLoss"] = merged["CurrentValue"] - merged["InvestedValue"]
    merged["ProfitLossPct"] = (merged["ProfitLoss"] / merged["InvestedValue"]) * 100

    summary = {
        "TotalInvested": merged["InvestedValue"].sum(),
        "CurrentValue": merged["CurrentValue"].sum(skipna=True),
        "NetPL": merged["ProfitLoss"].sum(skipna=True),
        "NetPLPct": (merged["ProfitLoss"].sum(skipna=True) / merged["InvestedValue"].sum()) * 100,
    }

    today = dt.date.today().strftime("%Y-%m-%d")
    merged.to_html(DAILY_REPORT_DIR / f"portfolio_report_{today}.html", index=False)

    return merged, summary

def load_week_from_sql():
    end = dt.date.today()
    start = end - dt.timedelta(days=7)
    conn = sqlite3.connect(DB_PATH)
    q = """
    SELECT RunDate, Ticker, Sector, Industry, Open, Close
    FROM daily_stocks
    WHERE RunDate BETWEEN ? AND ?
    """
    df = pd.read_sql_query(q, conn, params=(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
    conn.close()
    for col in ['Open', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def compute_weekly_returns(week_df):
    if week_df.empty:
        return pd.DataFrame(columns=['Ticker','Sector','Industry','WeeklyReturnPct'])

    agg = week_df.sort_values(['Ticker', 'RunDate']).groupby('Ticker').agg(
        FirstOpen=('Open', lambda s: s.dropna().iloc[0] if s.dropna().size else None),
        LastClose=('Close', lambda s: s.dropna().iloc[-1] if s.dropna().size else None),
        Sector=('Sector', 'last'),
        Industry=('Industry', 'last')
    ).reset_index()

    agg['WeeklyReturnPct'] = agg.apply(
        lambda row: ((row['LastClose'] - row['FirstOpen']) / row['FirstOpen'] * 100)
        if pd.notna(row['FirstOpen']) and row['FirstOpen'] != 0 and pd.notna(row['LastClose'])
        else None, axis=1
    )
    return agg[['Ticker','Sector','Industry','WeeklyReturnPct']]

def save_weekly_json(weekly_df):
    out_path = WEEKLY_REPORT_DIR / f"weekly_{dt.date.today()}.json"
    weekly_df.to_json(out_path, orient="records", indent=2)
    return str(out_path)
