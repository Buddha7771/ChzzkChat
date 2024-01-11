import requests


def fetch_chatChannelId(streamer:str) -> str :

    url = f'https://api.chzzk.naver.com/polling/v2/channels/{streamer}/live-status'
    try:
        response = requests.get(url).json()
        return response['content']['chatChannelId']
    except:
        raise ValueError(f'잘못된 입력값 : {streamer}')


def fetch_channelName(streamer:str) -> str :

    url = f'https://api.chzzk.naver.com/service/v1/channels/{streamer}'
    try:
        response = requests.get(url).json()
        return response['content']['channelName']
    except:
        raise ValueError(f'잘못된 입력값 : {streamer}')


def fetch_accessToken(chatChannelId, cookies:dict) -> str :

    url = f'https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={chatChannelId}&chatType=STREAMING'    
    try:
        response = requests.get(url, cookies=cookies).json()
        return response['content']['accessToken']
    except:
        raise ValueError(f'잘못된 입력값 : {chatChannelId}, {cookies}')


def fetch_userIdHash(cookies:dict) -> str :

    try:
        response = requests.get('https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus', cookies=cookies).json()
        return response['content']['userIdHash']
    except:
        raise ValueError(f'잘못된 입력값 : {cookies}')
    
