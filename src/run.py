import os
import time

from dotenv import load_dotenv
from schedule import (
    every,
    repeat,
    run_pending
)
from slack_bolt.adapter.socket_mode import SocketModeHandler

from atcoder_gacha_bot.app import app
from atcoder_gacha_bot.app import post_daily_problem


@repeat(every().day.at('09:00', 'Asia/Tokyo'))
def daily_job():
    post_daily_problem()


if __name__ == "__main__":
    load_dotenv()

    # ソケットモードサーバに接続
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).connect()

    while True:
        run_pending()   
        time.sleep(1)
