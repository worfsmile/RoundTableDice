# this file call the api to modify text

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import torch
from openai import OpenAI
from tqdm import tqdm
import random
from copy import deepcopy

from system_message import system_message

api_key = 'sk-251c110d2ce44b5b93e3618d3df0dc90'


def print_balance():
    url = "https://api.deepseek.com/user/balance"

    payload={}
    headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

def print_models():
    # for backward compatibility, you can still use `` as `base_url`.
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    print(client.models.list())

def api_call(messages: str) -> str:
    url = "https://api.deepseek.com/chat/completions"

    payload = json.dumps({
        "messages": messages,
        "model": "deepseek-chat",
        "frequency_penalty": 0,
        "max_tokens": 1024,
        "presence_penalty": 0,
        "response_format": {
            "type": "text"
        },
        "stop": None,
        "stream": False,
        "stream_options": None,
        "temperature": 0.5,
        "top_p": 1,
        "tools": None,
        "tool_choice": "none",
        "logprobs": False,
        "top_logprobs": None
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def prompter(context, dices, n=1):
    last = context[-1][1]
    l, k = last.dice_num, last.dice_point
    context_str = ["{c[1].dice_point} dices with {c[1].dice_num} points".format(c=c) for c in context]
    
    return f"""
    
    This is your turn, previous player's decision is: {context_str[-n:]}(from earlier to current). Your dices is {dices}.
    Please make a guess that there are l dice with k points, where (l > {l}) or (l == {l} and k > {k}), represented by (l, k).
    Or quesiton last player's decision, represented by (0, 0).

    reply with (l,k) or (0,0) 
    please only reply a tuple, without space inside.

    """

def LLMsResponse(context, dices, n = 1):   
    last = context[-1][1]
    message = [
        {
            "role": "system",
            "content": system_message(dices)
        },
        {
            "role": "user",
            "content": prompter(context, dices, n)
        }
    ]
    response = api_call(message)
    response = json.loads(response)
    message = response['choices'][0]['message']['content']
    try:
        if int(message) == 0:
            message = "(0, 0)"
    except:
        pass
    message_copy = deepcopy(message)
    flag = -1
    error_text = ""
    try:
        message = deepcopy(message_copy)
        if message.startswith("("):
            message = message[1:]
        if message.endswith(")"):
            message = message[:-1]
        l, k = message.split(",")
        k = int(k)
        l = int(l)
    except:
        try:
            message = deepcopy(message_copy)
            message = message.split(r"\n")[-1]
            if message.startswith("("):
                message = message[1:]
            if message.endswith(")"):
                message = message[:-1]
            l, k = message.split(",")
            k = int(k)
            l = int(l)
        except:
            try:
                message = deepcopy(message_copy)
                message = message.split(r"\n")[-1].split(" ")[-1]
                if message.startswith("("):
                    message = message[1:]
                if message.endswith(")"):
                    message = message[:-1]
                l, k = message.split(",")
                k = int(k)
                l = int(l)
            except:
                return flag, message_copy
    message = deepcopy(message_copy)
    if l == 0 and k == 0:
        flag = 0
        return flag, (0, 0)
    if k < 1 or k > 6:
        flag = 1
        error_text += "Invalid number of dice. Please enter a number between 1 and 6." + message
    elif l < last.dice_num or (l == last.dice_num and k <= last.dice_point):
        flag = 1
        error_text += f"Invalid assert. Please make a guess that there are l dice with k points, where (l > {last.dice_num}) or (l == {last.dice_num} and k > {last.dice_point})." + message
    else:
        flag = 0
    if flag:
        return flag, error_text
    return flag, (l, k)
    # flag = 0 means the response is correct, otherwise, means the response is incorrect.


if __name__ == '__main__':
    print_balance()