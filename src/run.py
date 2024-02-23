import os

from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler

from atcoder_gacha_bot.app import app


if __name__ == "__main__":
    load_dotenv()

    # アプリを起動
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
