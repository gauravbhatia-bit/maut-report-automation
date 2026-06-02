from apscheduler.schedulers.blocking import BlockingScheduler
from report_generator import generate_report
from datetime import datetime

def weekly_job():
    print(f"[{datetime.now()}] ⏰ Scheduler triggered — generating weekly report...")
    generate_report(week_label=f"Week of {datetime.now().strftime('%B %d, %Y')}")

if __name__ == "__main__":
    # Generate one report immediately on startup
    print("🚀 Generating initial report...")
    generate_report(week_label="Demo Report — Maut Analytics 2024")

    # Then schedule every Monday at 08:00
    scheduler = BlockingScheduler()
    scheduler.add_job(weekly_job, "cron", day_of_week="mon", hour=8, minute=0)
    print("⏰ Scheduler started — next run every Monday at 08:00")
    print("   Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped.")
