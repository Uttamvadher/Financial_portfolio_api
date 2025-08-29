import matplotlib.pyplot as plt
from config import DAILY_REPORT_DIR, WEEKLY_REPORT_DIR

def plot_daily_charts(df):
    if df.empty: return None
    for ticker in df["Ticker"].unique():
        sub = df[df["Ticker"] == ticker]
        plt.figure()
        plt.title(f"{ticker} Daily Close")
        plt.plot(sub["Close"])
        plt.savefig(DAILY_REPORT_DIR / f"{ticker}_daily.png")
        plt.close()

def plot_weekly_charts(weekly_df):
    if weekly_df.empty: return None
    plt.figure(figsize=(8, 4))
    plt.bar(weekly_df["Ticker"], weekly_df["WeeklyReturnPct"])
    plt.title("Weekly Returns")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(WEEKLY_REPORT_DIR / "weekly_returns.png")
    plt.close()
