import json
from dataclasses import dataclass, field

import requests

from .constant import CONFIG_PATH, HEADERS


@dataclass
class ChzzkApi:
    NID_AUT: str
    NID_SES: str
    session: requests.Session | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        self.session.headers.update(HEADERS)

        try:
            self.fetch_user_id_hash()
        except Exception as e:
            msg = "쿠키 정보가 올바르지 않습니다. 쿠키 정보를 다시 확인하세요"
            raise ValueError(msg) from e

    @property
    def cookies(self) -> dict[str, str]:
        return {
            "NID_AUT": self.NID_AUT,
            "NID_SES": self.NID_SES,
        }

    @classmethod
    def load(cls) -> "ChzzkApi":
        if not CONFIG_PATH.exists():
            msg = "설정 파일이 존재하지 않습니다. 먼저 'chzzkchat login' 명령어를 사용하여 쿠키를 저장하세요."
            raise FileNotFoundError(msg)
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            cookies = json.load(f)
            return cls(**cookies)

    def save(self) -> None:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(self.cookies, f, ensure_ascii=False, indent=4)

    def fetch_chat_channel_id(self, streamer_id: str) -> str:
        url = (
            f"https://api.chzzk.naver.com/polling/v2/channels/{streamer_id}/live-status"
        )
        error_msg = "채팅 채널 ID를 가져오는 데 실패했습니다. 쿠키 정보 또는 스트리머 ID가 올바른지 확인하세요."

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response = response.json()
            chat_channel_id = response["content"]["chatChannelId"]
        except requests.RequestException as e:
            raise requests.RequestException(error_msg) from e
        except KeyError as e:
            raise KeyError(error_msg) from e

        if chat_channel_id is None:
            raise ValueError(error_msg)
        return chat_channel_id

    def fetch_channel_name(self, streamer_id: str) -> str:
        url = f"https://api.chzzk.naver.com/service/v1/channels/{streamer_id}"
        error_msg = "채널 정보를 가져오는 데 실패했습니다. 쿠키 정보 또는 스트리머 ID가 올바른지 확인하세요."

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response = response.json()
            channel_name = response["content"]["channelName"]
        except requests.RequestException as e:
            raise requests.RequestException(error_msg) from e
        except KeyError as e:
            raise KeyError(error_msg) from e

        if channel_name is None:
            raise ValueError(error_msg)
        return channel_name

    def fetch_access_token(self, chat_channel_id: str) -> tuple[str, str]:
        url = "https://comm-api.game.naver.com/nng_main/v1/chats/access-token"
        error_msg = "AccessToken을 가져오는 데 실패했습니다. 쿠키 정보 또는 채팅 채널 ID가 올바른지 확인하세요."
        params = {"channelId": chat_channel_id, "chatType": "STREAMING"}

        try:
            response = self.session.get(url, timeout=10, params=params)
            response.raise_for_status()
            response = response.json()
            access_token = response["content"]["accessToken"]
            extra_token = response["content"]["extraToken"]
        except requests.RequestException as e:
            raise requests.RequestException(error_msg) from e
        except KeyError as e:
            raise KeyError(error_msg) from e

        if access_token is None or extra_token is None:
            raise ValueError(error_msg)
        return access_token, extra_token

    def fetch_user_id_hash(self) -> str:
        url = "https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus"
        error_msg = "사용자 ID 해시를 가져오는 데 실패했습니다. 쿠키 정보가 올바른지 확인하세요."

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response = response.json()
            user_id_hash = response["content"]["userIdHash"]
        except requests.RequestException as e:
            raise requests.RequestException(error_msg) from e
        except KeyError as e:
            raise KeyError(error_msg) from e

        if user_id_hash is None:
            raise ValueError(error_msg)
        return user_id_hash
