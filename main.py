#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 22:54:24 2022

@author: Alexander Mikhailov
"""

import threading
import time
import urllib.parse
import webbrowser
from functools import wraps
from http import HTTPStatus
from typing import Callable, Optional

import requests
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from flask import Flask, request

# === Configuration ===
AUTH_BASE_URL = 'https://hh.ru/oauth/authorize'
TOKEN_URL = 'https://hh.ru/oauth/token'
AUTH_PAYLOAD = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI
}
PORT = 8080

app = Flask(__name__)
auth_code_container = {'code': None}

# Token storage
token_data = {
    'access_token': None,
    'refresh_token': None,
    'expires_at': 0
}


# === Step 1: OAuth start ===


def start_oauth_and_get_tokens() -> Optional[dict]:
    auth_url = f'{AUTH_BASE_URL}?{urllib.parse.urlencode(AUTH_PAYLOAD)}'
    threading.Thread(target=lambda: app.run(port=PORT), daemon=True).start()
    webbrowser.open(auth_url)
    print('Waiting for user authorization...')

    while auth_code_container['code'] is None:
        time.sleep(0.5)  # Avoid busy loop

    tokens = exchange_code_for_token(
        auth_code=auth_code_container['code'],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )

    if tokens:
        store_token_data(tokens)
    return tokens


def exchange_code_for_token(
    auth_code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> Optional[dict]:
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == HTTPStatus.OK:
        return response.json()
    print('Token exchange failed:', response.status_code, response.text)
    return None


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization code not found.', HTTPStatus.BAD_REQUEST
    auth_code_container['code'] = code
    return 'Authorization complete. You can close this tab.'


# === Step 2: Token refresh logic ===
def store_token_data(tokens: dict):
    token_data['access_token'] = tokens['access_token']
    token_data['refresh_token'] = tokens.get('refresh_token')
    expires_in = tokens.get('expires_in', 3600)
    token_data['expires_at'] = time.time() + expires_in


def refresh_access_token():
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token_data['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == HTTPStatus.OK:
        print('Access token refreshed.')
        store_token_data(response.json())
    else:
        print('Token refresh failed:', response.status_code, response.text)


def get_valid_access_token() -> str:
    if time.time() >= token_data['expires_at']:
        print('Access token expired — refreshing...')
        refresh_access_token()
    return token_data['access_token']


# === Step 3: Decorator to ensure token is valid ===
def with_valid_token(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # =====================================================================
        # OAuth2 Access Token
        # =====================================================================
        headers = {'Authorization': f'Bearer {get_valid_access_token()}'}
        return func(*args, headers=headers, **kwargs)
    return wrapper


# === Example API calls ===
@with_valid_token
def get_my_resumes(headers):
    url = 'https://api.hh.ru/resumes/mine'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


@with_valid_token
def get_recommended_vacancies(resume_id: str, headers):
    url = f'https://api.hh.ru/resumes/{resume_id}/recommendations'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    start_oauth_and_get_tokens()
    resumes = get_my_resumes()
    if not resumes.get('items'):
        print('No resumes found.')
    else:
        resume_id = resumes['items'][0]['id']
        print(f'Using resume ID: {resume_id}')

        vacancies = get_recommended_vacancies(resume_id)
        for vacancy in vacancies.get('items', []):
            print(vacancy['name'], '-', vacancy['alternate_url'])
