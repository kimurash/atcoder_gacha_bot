import os
import re
from random import choice

import requests

from dotenv import find_dotenv
from dotenv import load_dotenv
from slack_bolt import App


load_dotenv(find_dotenv())

# ボットトークンを使ってアプリを初期化
app = App(token=os.getenv('SLACK_BOT_TOKEN'))

@app.message('hello')
def handle_hello_msg(ack, message, say):
    ack()

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
def handle_gacha_cmd(args):
    args.ack()

    option = args.command['text']
    problem = select_problem(option)
    if problem is None:
        return

    diff = get_problem_diff(problem['id'])

    args.say(
        blocks=make_msg_block(problem, diff),
        text=problem['title']
    )


def post_daily_problem():
    problem = select_problem()
    if problem is None:
        return
    
    diff = get_problem_diff(problem['id'])
    msg_block = make_msg_block(problem, diff)

    title_txt_path = (
        os.path.join(
            os.path.dirname(__file__),
            'daily_post_title.txt'
        )
    )
    with open(title_txt_path, 'r') as f:
        daily_post_title = f.read()
        msg_block = [
            {
                'type': 'section',
                'text': {
                    'type': 'plain_text',
                    'text': daily_post_title,
                }
            }
        ] + msg_block

    app.client.chat_postMessage(
        channel=os.getenv('CHANNEL_ID'),
        blocks=msg_block,
        text=problem['title']
    )


def make_msg_block(problem: dict, diff: str):
    title = f"{problem['contest_id'].upper()} / {problem['title']}"
    point = problem['point']
    if point is not None:
        point = int(point)
    url = f"https://atcoder.jp/contests/{problem['contest_id']}/tasks/{problem['id']}"

    return [
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
                'text': f"<{url}|Visit problem page>"
            }
        }
    ]


def select_problem(option=''):
    response = requests.get(os.getenv('AP_PROBLEM_URL'))
    if not check_status_code(response):
        app.client.chat_postMessage(
            channel=os.getenv('CHANNEL_ID'),
            text="問題の取得に失敗しました"
        )
        return None

    prob_list = response.json()
    cand_prob = filter_problem(prob_list, option)
    rand_prob = choice(cand_prob)
    
    return rand_prob


def filter_problem(prob_list: list, option: str):
    if len(option) != 1:
        return prob_list
    
    if not re.match(r'^[a-gA-G]$', option):
        return prob_list
    
    cand_prob = list()
    for prob in prob_list:
        if 'problem_index' in prob:
            if prob['problem_index'] == option:
                cand_prob.append(prob)

    return cand_prob


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
