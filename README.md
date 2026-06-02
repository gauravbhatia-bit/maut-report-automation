# Automated Maut Weekly Report Generator

Automated weekly KPI reporting pipeline for German highway toll analytics.
Generates professional HTML reports with interactive Plotly charts every Monday via APScheduler.

## Tools
- APScheduler, Plotly, Jinja2, DuckDB, Python, Pandas

## How to Run
pip install -r requirements.txt
python report_scheduler.py

## Project Structure
- data_generator.py       - Synthetic toll data
- report_generator.py     - SQL queries + Plotly + Jinja2
- report_scheduler.py     - Runs every Monday 08:00
- templates/              - HTML report template
- reports/                - Auto-generated HTML reports

Gaurav Bhatia | MSc Data Science, GISMA University Berlin | 2026
