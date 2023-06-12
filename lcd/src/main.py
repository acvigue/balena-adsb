from signal import signal, SIGTERM, SIGHUP, pause
import os
import schedule
from urllib.request import urlopen
import json
from time import sleep
from lcd import LCD

lcd = LCD()
url = os.environ['FA_AIRCRAFT_URL']
airdata = None
last_msgs = 0
screen_no = 0
max_screens = 3


def fetch_airdata():
    global airdata, last_msgs
    with urlopen(url) as conn:
        try:
            data = conn.read()
            encoding = conn.info().get_content_charset('utf-8')

            if airdata is not None:
                last_msgs = airdata["messages"]

            airdata = json.loads(data.decode(encoding))
        except Exception:
            airdata = None


def switch_screen():
    global max_screens, screen_no
    screen_no = screen_no + 1
    if screen_no >= max_screens:
        screen_no = 0
# curl "$BALENA_SUPERVISOR_ADDRESS/v2/device/name?apikey=$BALENA_SUPERVISOR_API_KEY"


def show_screen():
    if screen_no == 0:
        if airdata is not None:
            lcd.text("Aircraft: {}".format(len(airdata["aircraft"])), 1)
            lcd.text("Msgs/s: {}".format(airdata["messages"] - last_msgs), 2)
        else:
            lcd.text("Uplink err..", 1)
    elif screen_no == 1:
        nameurl = f"{os.environ['BALENA_SUPERVISOR_ADDRESS']}/v2/device/name?apikey={os.environ['BALENA_SUPERVISOR_API_KEY']}"
        with urlopen(nameurl) as conn:
            data = conn.read()
            encoding = conn.info().get_content_charset('utf-8')
            data = json.loads(data.decode(encoding))
            lcd.text("Device name:", 1)
            lcd.text(data['deviceName'], 2)
    elif screen_no == 2:
        vpnurl = f"{os.environ['BALENA_SUPERVISOR_ADDRESS']}/v2/device/vpn?apikey={os.environ['BALENA_SUPERVISOR_API_KEY']}"
        with urlopen(vpnurl) as conn:
            data = conn.read()
            encoding = conn.info().get_content_charset('utf-8')
            data = json.loads(data.decode(encoding))
            lcd.text("Cloud status:", 1)
            lcd.text('connected' if data['vpn']['connected'] else 'disconnected', 2)


schedule.every(3).seconds.do(fetch_airdata)
schedule.every(2).seconds.do(show_screen)
schedule.every(4).seconds.do(switch_screen)


def safe_exit(signum, frame):
    exit(1)


try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    while True:
        schedule.run_pending()
        sleep(1)
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
