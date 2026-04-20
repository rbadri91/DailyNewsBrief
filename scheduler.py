"""
Local APScheduler daemon for DailyNewsBrief.

Runs the briefing pipeline on a schedule defined in preferences.yaml:
  - Daily at `email.send_time` in `email.timezone`
  - Stock analysis included on `email.stock_day`

Usage:
  python scheduler.py          # start the scheduler (runs until Ctrl+C)
  python scheduler.py --now    # run once immediately then exit
"""

import argparse
import logging
import signal
import sys
from datetime import datetime

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from main import load_preferences, run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def _parse_send_time(send_time: str) -> tuple[int, int]:
    """Parse 'HH:MM' into (hour, minute)."""
    parts = send_time.split(":")
    return int(parts[0]), int(parts[1])


def scheduled_run():
    log.info("Scheduler triggered — starting briefing pipeline")
    try:
        run()
        log.info("Briefing pipeline completed successfully")
    except Exception as e:
        log.error(f"Briefing pipeline failed: {e}", exc_info=True)


def start_scheduler():
    prefs = load_preferences()
    email_cfg = prefs.get("email", {})
    send_time = email_cfg.get("send_time", "07:00")
    timezone = email_cfg.get("timezone", "America/New_York")

    hour, minute = _parse_send_time(send_time)

    scheduler = BlockingScheduler(timezone=timezone)
    scheduler.add_job(
        scheduled_run,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
        id="daily_brief",
        name="Daily News Brief",
        misfire_grace_time=300,  # allow up to 5 min late start
    )

    log.info(f"Scheduler started — daily brief at {send_time} {timezone}")
    log.info("Press Ctrl+C to stop")

    def _shutdown(signum, frame):
        log.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    scheduler.start()


def main():
    parser = argparse.ArgumentParser(description="DailyNewsBrief local scheduler")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run the briefing pipeline once immediately and exit",
    )
    args = parser.parse_args()

    if args.now:
        log.info("Running briefing pipeline immediately (--now flag)")
        run()
    else:
        start_scheduler()


if __name__ == "__main__":
    main()
