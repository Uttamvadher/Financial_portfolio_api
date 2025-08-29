import yfinance as yf
import pandas as pd
import datetime as dt

def get_stock_info(portfolio):
    rows = []
    run_ts = dt.datetime.now()
    run_date = run_ts.strftime("%Y-%m-%d")

    for stock_item in portfolio:
        ticker = stock_item["Ticker"]
        qty = stock_item["Quantity"]
        buy_price = stock_item["BuyPrice"]

        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            
            # Skip if the ticker has no market data
            if 'regularMarketPrice' not in info:
                continue  # Ignore this ticker

            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')

            hist = stock.history(period='1d', interval='5m')
            if not hist.empty:
                open_price = float(hist['Open'].iloc[0])
                close_price = float(hist['Close'].iloc[-1])
                high, low = float(hist['High'].max()), float(hist['Low'].min())
                fluctuation = high - low
                perf = ((close_price - open_price) / open_price) * 100
            else:
                open_price = close_price = high = low = fluctuation = perf = None

            investment = qty * buy_price
            current_value = qty * close_price if close_price else None
            pnl = (current_value - investment) if current_value else None
            pnl_pct = (pnl / investment * 100) if pnl else None

            rows.append({
                'RunDate': run_date,
                'RunTimestamp': run_ts.isoformat(timespec='seconds'),
                'Ticker': ticker,
                'Sector': sector,
                'Industry': industry,
                'Open': open_price,
                'Close': close_price,
                'High': high,
                'Low': low,
                'Fluctuation': fluctuation,
                'PerformancePct': perf,
                'Quantity': qty,
                'BuyPrice': buy_price,
                'Investment': investment,
                'CurrentValue': current_value,
                'PnL': pnl,
                'PnLPct': pnl_pct
            })
        except Exception:
            # Skip tickers that throw exceptions (invalid / inactive)
            continue

    return pd.DataFrame(rows)
