import os
from random import choice

import requests
from dotenv import find_dotenv
from dotenv import load_dotenv
from slack_bolt import App


load_dotenv(find_dotenv())

# ボットトークンとソケットモードハンドラを使ってアプリを初期化
app = App(token=os.getenv('SLACK_BOT_TOKEN'))

@app.message('hello')
def message_hello(message, say):
    say(
        blocks=[
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"Hey there <@{message['user']}>!"
                }
            }
        ],
        # NOTE:text引数は常に指定が推奨
        text=f"Hey there <@{message['user']}>!"
    )


@app.command('/gacha')
def handle_gacha_command(args):
    args.ack()

    problem = select_problem()
    diff = get_problem_diff(problem['id'])
    if diff is not None:
        diff = diff.get('difficulty', 'unknown')

    title = f"{problem['contest_id'].upper()} / {problem['title']}"
    point = int(problem['point']) if problem['point'] else 'unknown'
    url = f"https://atcoder.jp/contests/{problem['contest_id']}/tasks/{problem['id']}"

    args.say(
        blocks=[
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': title,
                }
            },
            {
                "type": "divider"
            },
            {
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f'*point:*\n{point}'
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f'*difficulty:*\n{diff}'
                    }
                ]
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"<{url}|View problem page>"
                }
            }
        ],
        text=problem['title']
    )


def select_problem():
    # FIXME:正常なレスポンスが返ってくる前提
    response = requests.get(os.getenv('AP_PROBLEM_URL'))
    prob_list = response.json()
    rand_prob = choice(prob_list)
    return rand_prob


def get_problem_diff(prob_id: str):
    # FIXME:正常なレスポンスが返ってくる前提
    response = requests.get(os.getenv('AP_DIFF_URL'))
    est_diff = response.json()
    if prob_id in est_diff:
        return est_diff[prob_id]
    else:
        return None