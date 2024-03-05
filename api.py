import requests


def fetch_chatChannelId(streamer: str) -> str:
    url = f'https://api.chzzk.naver.com/polling/v2/channels/{streamer}/live-status'
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers).json()
        return response['content']['chatChannelId']
    except:
        raise ValueError(f'잘못된 입력값 : {streamer}')


def fetch_channelName(streamer: str) -> str:
    url = f'https://api.chzzk.naver.com/service/v1/channels/{streamer}'
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers).json()
        return response['content']['channelName']
    except:
        raise ValueError(f'잘못된 입력값 : {streamer}')


def fetch_accessToken(chatChannelId, cookies: dict) -> str:
    url = f'https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={chatChannelId}&chatType=STREAMING'
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        response = requests.get(url, cookies=cookies, headers=headers).json()
        return response['content']['accessToken'], response['content']['extraToken']
    except:
        raise ValueError(f'잘못된 입력값 : {chatChannelId}, {cookies}')


def fetch_userIdHash(cookies: dict) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        response = requests.get('https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus', cookies=cookies,
                                headers=headers).json()
        return response['content']['userIdHash']
    except:
        raise ValueError(f'잘못된 입력값 : {cookies}')
