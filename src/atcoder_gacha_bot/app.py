import os
from random import choice

import requests
from dotenv import find_dotenv
from dotenv import load_dotenv
from slack_bolt import App


load_dotenv(find_dotenv())

# ボットトークンを使ってアプリを初期化
app = App(token=os.getenv('SLACK_BOT_TOKEN'))

@app.message('hello')
def handle_msg_hello(msg, say):
    say(
        blocks=[
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"Hey there <@{msg['user']}>!"
                }
            }
        ],
        # NOTE:text引数は常に指定が推奨
        text=f"Hey there <@{msg['user']}>!"
    )


@app.command('/gacha')
def handle_gacha_cmd(args):
    args.ack()

    problem = select_problem()
    if problem is None:
        args.say("問題の取得に失敗しました")
        return

    diff = get_problem_diff(problem['id'])

    title = f"{problem['contest_id'].upper()} / {problem['title']}"
    point = problem['point']
    if point is not None:
        point = int(point)
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
    response = requests.get(os.getenv('AP_PROBLEM_URL'))
    if not check_status_code(response):
        return None

    prob_list = response.json()
    rand_prob = choice(prob_list)
    return rand_prob


def get_problem_diff(prob_id: str):
    response = requests.get(os.getenv('AP_DIFF_URL'))
    if not check_status_code(response):
        return None

    diff_dict = response.json()
    if prob_id in diff_dict:
        est_diff = diff_dict[prob_id]
        return est_diff.get('difficulty', 'unknown')
    else:
        return None

def check_status_code(response: requests.Response):
    match response.status_code:
        case 200:
            return True
        case _:
            return False
