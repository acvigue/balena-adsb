from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
import os
import time
from urllib.request import urlopen
import json

url = os.environ['FA_AIRCRAFT_URL']

lcd = LCD()
def safe_exit(signum, frame):
    exit(1)
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    while True:
        with urlopen(url) as conn:
            data = conn.read()
            encoding = conn.info().get_content_charset('utf-8')
            data = json.loads(data.decode(encoding))
            lcd.text("Aircraft: {}".format(len(data["aircraft"])), 1)
            lcd.text("Msg: {}".format(data["messages"]), 2)
        time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()