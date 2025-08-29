def print_sector_breakdown(df):
    if df.empty: return {}
    breakdown = df.groupby("Sector")["Investment"].sum().to_dict()
    print("Sector Breakdown:", breakdown)
    return breakdown

def print_top_movers(df, n=5):
    if df.empty: return {}
    movers = df.sort_values("PnLPct", ascending=False).head(n)
    print("Top Movers:", movers[["Ticker", "PnLPct"]])
    return movers.to_dict(orient="records")
