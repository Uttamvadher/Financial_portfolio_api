from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from data_fetch import get_stock_info
from storage import save_to_sql, save_to_json, save_to_mongo
from reports import generate_portfolio_report, load_week_from_sql, compute_weekly_returns
from analysis import print_sector_breakdown, print_top_movers
from charts import plot_daily_charts, plot_weekly_charts
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import datetime as dt



app = FastAPI(title="Portfolio Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow any origin (browser)
    allow_credentials=True,
    allow_methods=["*"],       # Allow POST, GET, etc.
    allow_headers=["*"],       # Allow headers like Content-Type
)


# ---------- MODELS ----------
class StockItem(BaseModel):
    Ticker: str
    Quantity: int
    BuyPrice: float

class PortfolioRequest(BaseModel):
    portfolio: List[StockItem]


# ---------- ENDPOINTS ----------

@app.post("/fetch")
def fetch_data(req: PortfolioRequest):
    """Fetch stock info from Yahoo Finance"""
    df = get_stock_info([s.dict() for s in req.portfolio])
    save_to_sql(df)
    save_to_json(df)
    mongo_status = save_to_mongo(df)
    return {"status": "ok", "mongo": mongo_status, "rows": df.to_dict(orient="records")}


@app.post("/report/daily")
def daily_report(req: PortfolioRequest):
    df = get_stock_info([s.dict() for s in req.portfolio])
    merged, summary = generate_portfolio_report(df, [s.dict() for s in req.portfolio])
    plot_daily_charts(df)
    return {"summary": summary, "report_file": "reports/daily"}


@app.get("/report/weekly")
def weekly_report():
    week_df = load_week_from_sql()
    weekly = compute_weekly_returns(week_df)
    plot_weekly_charts(weekly)
    return {"weekly_returns": weekly.to_dict(orient="records")}

def run_daily_report():
    print(f"[{dt.datetime.now()}] Running daily scheduled report...")
    portfolio = load_portfolio_from_sql()  
    df = get_stock_info(portfolio)
    merged, summary = generate_portfolio_report(df, portfolio)
    plot_daily_charts(df)
    print("Daily report generated:", summary)


def run_weekly_report():
    print(f"[{dt.datetime.now()}] Running weekly scheduled report...")
    week_df = load_week_from_sql()
    weekly = compute_weekly_returns(week_df)
    plot_weekly_charts(weekly)
    print("Weekly report generated.")



scheduler = BackgroundScheduler()
scheduler.add_job(run_daily_report, "cron", day_of_week="mon-fri", hour=16, minute=0)
scheduler.add_job(run_weekly_report, "cron", day_of_week="fri", hour=16, minute=0)
scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.post("/analysis/sector")
def sector_analysis(req: PortfolioRequest):
    df = get_stock_info([s.dict() for s in req.portfolio])
    breakdown = print_sector_breakdown(df)
    return {"sector_breakdown": breakdown}


@app.post("/analysis/topmovers")
def top_movers(req: PortfolioRequest, n: int = 5):
    df = get_stock_info([s.dict() for s in req.portfolio])
    movers = print_top_movers(df, n=n)
    return {"top_movers": movers}
