import requests

HEADERS = {'User-Agent': ''}

def fetch_chatChannelId(streamer: str, cookies: dict) -> str:
    url = f'https://api.chzzk.naver.com/polling/v2/channels/{streamer}/live-status'
    try:
        response = requests.get(url, cookies=cookies, headers=HEADERS)
        response.raise_for_status()
        response = response.json()
        
        chatChannelId = response['content']['chatChannelId']
        assert chatChannelId!=None
        return chatChannelId
    except Exception as e:
        raise e

def fetch_channelName(streamer: str) -> str:
    url = f'https://api.chzzk.naver.com/service/v1/channels/{streamer}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        response = response.json()
        return response['content']['channelName']
    except Exception as e:
        raise e


def fetch_accessToken(chatChannelId, cookies: dict) -> str:
    url = f'https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={chatChannelId}&chatType=STREAMING'
    try:
        response = requests.get(url, cookies=cookies, headers=HEADERS)
        response.raise_for_status()
        response = response.json()
        return response['content']['accessToken'], response['content']['extraToken']
    except Exception as e:
        raise e


def fetch_userIdHash(cookies: dict) -> str:
    url = 'https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus'
    try:
        response = requests.get(url, cookies=cookies, headers=HEADERS)
        response.raise_for_status()
        response = response.json()
        return response['content']['userIdHash']
    except Exception as e:
        raise e
