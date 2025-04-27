from apscheduler.schedulers.blocking import BlockingScheduler
from agent.standup_agent import AutoStandupAgent

def scheduled_job():
    agent = AutoStandupAgent()
    agent.run()


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, 'cron', hour=22, minute=53)  # Daily at 9AM
    print("Scheduler started...")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped manually")
        scheduler.shutdown()