import duckdb
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
from data_generator import generate_toll_database

def get_kpis(con):
    return con.execute(
        "SELECT COUNT(DISTINCT transaction_id) AS total_tx,"
        " ROUND(SUM(toll_amount),2) AS total_revenue,"
        " ROUND(AVG(toll_amount),4) AS avg_toll,"
        " COUNT(DISTINCT segment_id) AS segments,"
        " COUNT(DISTINCT vehicle_id) AS vehicles"
        " FROM toll_transactions"
    ).fetchdf().iloc[0]

def chart_revenue_by_segment(con):
    df = con.execute(
        "SELECT s.segment_name, ROUND(SUM(t.toll_amount),2) AS revenue"
        " FROM toll_transactions t JOIN segments s ON t.segment_id=s.segment_id"
        " GROUP BY s.segment_name ORDER BY revenue DESC"
    ).fetchdf()
    fig = px.bar(df, x="segment_name", y="revenue",
                 color="revenue", color_continuous_scale="Blues",
                 labels={"segment_name":"Segment","revenue":"Revenue (€)"},
                 title="Total Revenue by Highway Segment")
    fig.update_layout(showlegend=False, plot_bgcolor="white",
                      font=dict(family="Arial", size=13))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def chart_weekly_trend(con):
    df = con.execute(
        "SELECT c.week_number AS week, ROUND(SUM(t.toll_amount),2) AS revenue"
        " FROM toll_transactions t JOIN calendar c ON t.date_id=c.date_id"
        " GROUP BY c.week_number ORDER BY week"
    ).fetchdf()
    fig = px.line(df, x="week", y="revenue", markers=True,
                  labels={"week":"Week Number","revenue":"Revenue (€)"},
                  title="Weekly Revenue Trend (Jan–Jun 2024)")
    fig.update_traces(line_color="#1f77b4", line_width=2.5)
    fig.update_layout(plot_bgcolor="white", font=dict(family="Arial", size=13))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def chart_peak_hours(con):
    df = con.execute(
        "SELECT t.hour, COUNT(*) AS transactions"
        " FROM toll_transactions t"
        " GROUP BY t.hour ORDER BY t.hour"
    ).fetchdf()
    colors = ["#d62728" if (7<=h<=9 or 17<=h<=19) else
              "#aec7e8" if (h>=22 or h<=5) else "#1f77b4"
              for h in df["hour"]]
    fig = go.Figure(go.Bar(x=df["hour"], y=df["transactions"],
                           marker_color=colors))
    fig.update_layout(title="Traffic Volume by Hour of Day",
                      xaxis_title="Hour", yaxis_title="Transactions",
                      plot_bgcolor="white", font=dict(family="Arial", size=13))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def chart_vehicle_class(con):
    df = con.execute(
        "SELECT v.vehicle_class, COUNT(*) AS transactions,"
        " ROUND(SUM(t.toll_amount),2) AS revenue"
        " FROM toll_transactions t JOIN vehicles v ON t.vehicle_id=v.vehicle_id"
        " GROUP BY v.vehicle_class ORDER BY revenue DESC"
    ).fetchdf()
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Transactions by Vehicle Class",
                                        "Revenue by Vehicle Class"),
                        specs=[[{"type":"pie"},{"type":"pie"}]])
    fig.add_trace(go.Pie(labels=df["vehicle_class"], values=df["transactions"],
                         name="Transactions"), row=1, col=1)
    fig.add_trace(go.Pie(labels=df["vehicle_class"], values=df["revenue"],
                         name="Revenue"), row=1, col=2)
    fig.update_layout(title="Vehicle Class: Traffic vs Revenue Share",
                      font=dict(family="Arial", size=13))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def top_segments_table(con):
    return con.execute(
        "SELECT s.segment_name AS Segment, s.toll_zone AS Zone,"
        " COUNT(t.transaction_id) AS Transactions,"
        " ROUND(SUM(t.toll_amount),2) AS Revenue_EUR,"
        " ROUND(AVG(t.toll_amount),4) AS Avg_Toll_EUR"
        " FROM toll_transactions t JOIN segments s ON t.segment_id=s.segment_id"
        " GROUP BY s.segment_name, s.toll_zone ORDER BY Revenue_EUR DESC"
    ).fetchdf()

def generate_report(week_label=None, output_dir="reports"):
    con = generate_toll_database()
    kpis = get_kpis(con)
    week_label = week_label or datetime.now().strftime("Week of %B %d, %Y")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report_template.html")

    html = template.render(
        week_label=week_label,
        generated_at=generated_at,
        total_tx=f"{int(kpis.total_tx):,}",
        total_revenue=f"€{float(kpis.total_revenue):,.2f}",
        avg_toll=f"€{float(kpis.avg_toll):.4f}",
        segments=int(kpis.segments),
        vehicles=int(kpis.vehicles),
        chart_revenue=chart_revenue_by_segment(con),
        chart_trend=chart_weekly_trend(con),
        chart_hours=chart_peak_hours(con),
        chart_vehicle=chart_vehicle_class(con),
        table_html=top_segments_table(con).to_html(
            index=False, classes="kpi-table", border=0)
    )

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/maut_report_{datetime.now().strftime('%Y-%m-%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Report saved: {filename}")
    return filename
