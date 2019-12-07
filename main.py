import re
import yaml
import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from notifiers import get_notifier

monitor_status = {}
config = None


def run_monitor(monitor):
    print("Executing monitor {}".format(monitor["name"]))

    matched = False

    result = requests.get(monitor["url"])
    soup = BeautifulSoup(result.content, "html.parser")

    for selected in soup.select(monitor["pattern"]["selector"]):
        if re.match(monitor["pattern"]["regex"], selected.text):
            matched = True

    should_alert = (matched and monitor["alert_when"] == "present") or \
                   (not matched and monitor["alert_when"] == "absent")

    if not should_alert and monitor["name"] in monitor_status:
        del monitor_status[monitor["name"]]
        print("Monitor {} is back to idle state".format(monitor["name"]))
    elif should_alert and monitor["name"] not in monitor_status:
        message = "Monitor {} has been triggered!\n\n{}".format(monitor["name"], monitor["url"])

        print("Monitor {} has been triggered!".format(monitor["name"]))

        if "telegram" in config["notifiers"]:
            telegram_config = config["notifiers"]["telegram"]
            telegram = get_notifier('telegram')
            telegram.notify(chat_id=telegram_config["chat_id"], token=telegram_config["bot_token"], message=message)
            print("Notified user via telegram")

        monitor_status[monitor["name"]] = datetime.now()
    else:
        print("State of monitor {} is unchanged".format(monitor["name"]))


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    for monitor_config in config["monitors"]:
        interval = monitor_config["interval"]

        if interval.endswith("w"):
            scheduler.add_job(run_monitor, 'interval', weeks=int(interval[:-1]), args=(monitor_config,))
        elif interval.endswith("d"):
            scheduler.add_job(run_monitor, 'interval', days=int(interval[:-1]), args=(monitor_config,))
        elif interval.endswith("h"):
            scheduler.add_job(run_monitor, 'interval', hours=int(interval[:-1]), args=(monitor_config,))
        elif interval.endswith("m"):
            scheduler.add_job(run_monitor, 'interval', minutes=int(interval[:-1]), args=(monitor_config,))
        elif interval.endswith("s"):
            scheduler.add_job(run_monitor, 'interval', seconds=int(interval[:-1]), args=(monitor_config,))
        else:
            print("Failed to setup job {}: Could not parse interval".format(monitor_config["name"]))

        run_monitor(monitor_config)

    print("Initialized {} monitors".format(len(config["monitors"])))

    scheduler.start()
