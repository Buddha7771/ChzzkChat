import json
import sys
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from websocket import WebSocket

from .api import ChzzkApi
from .constant import NICKNAME_PALLETTE, ChzzkChatCmd, ChzzkColor

KST = timezone(timedelta(hours=9))


@dataclass
class ChzzkChatMessage:
    chat_type: ChzzkChatCmd
    nickname: str
    message: str
    timestamp: str
    uid: str
    chat_channel_id: str
    subscribed: bool = False
    donated: bool = False
    payamount: int | None = None

    def get_rgb_code(self) -> tuple[int, int, int]:
        if self.uid == "anonymous":
            return ChzzkColor.VIOLET.value

        hash_value = 0
        for char in self.uid + self.chat_channel_id:
            hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF
        hash_value = abs(hash_value)
        hex_color = NICKNAME_PALLETTE[hash_value % len(NICKNAME_PALLETTE)]
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def is_system(self) -> bool:
        return self.uid == "SYSTEM_MESSAGE"


class ChzzkChatClient:
    def __init__(
        self,
        streamer_id: str,
        api: ChzzkApi | None = None,
    ) -> None:
        self.streamer_id = streamer_id
        self.api = api or ChzzkApi.load()

        self.userIdHash = self.api.fetch_user_id_hash()
        self.channelName = self.api.fetch_channel_name(streamer_id)
        self.accessToken = None
        self.extraToken = None
        self.chatChannelId = None
        self.sid = None
        self.sock: WebSocket | None = None

        self.connect()

    @property
    def default_dict(self) -> dict:
        return {
            "ver": "2",
            "svcid": "game",
            "cid": self.chatChannelId,
        }

    def _send(self, data: dict) -> None:
        if not self.sock or not self.sock.connected:
            msg = "채팅 서버에 연결되어 있지 않습니다."
            raise ConnectionError(msg)
        self.sock.send(json.dumps(data))

    def _recv(self) -> dict:
        if not self.sock or not self.sock.connected:
            msg = "채팅 서버에 연결되어 있지 않습니다."
            raise ConnectionError(msg)
        try:
            raw_message = self.sock.recv()
        except KeyboardInterrupt:
            sys.exit(0)
        except ConnectionError:
            self.connect()
            raw_message = self.sock.recv()
        return json.loads(raw_message)

    def connect(self) -> None:
        self.chatChannelId = self.api.fetch_chat_channel_id(self.streamer_id)
        self.accessToken, self.extraToken = self.api.fetch_access_token(
            self.chatChannelId,
        )

        self.sock = WebSocket()
        self.sock.connect("wss://kr-ss1.chat.naver.com/chat")

        self._send(
            {
                **self.default_dict,
                "cmd": ChzzkChatCmd.CONNECT.value,
                "tid": 1,
                "bdy": {
                    "uid": self.userIdHash,
                    "devType": 2001,
                    "accTkn": self.accessToken,
                    "auth": "SEND",
                },
            },
        )
        response = self._recv()
        self.sid = response["bdy"]["sid"]

        self._send(
            {
                **self.default_dict,
                "cmd": ChzzkChatCmd.REQUEST_RECENT_CHAT.value,
                "tid": 2,
                "sid": self.sid,
                "bdy": {"recentMessageCount": 50},
            },
        )
        self._recv()

        if not self.sock.connected:
            msg = f"{self.channelName} 채팅 서버에 연결할 수 없습니다."
            raise ValueError(msg)

    def chat(self, message: str) -> None:
        extras = {
            "chatType": "STREAMING",
            "emojis": "",
            "osType": "PC",
            "extraToken": self.extraToken,
            "streamingChannelId": self.chatChannelId,
        }
        self._send(
            {
                **self.default_dict,
                "tid": 3,
                "cmd": ChzzkChatCmd.SEND_CHAT.value,
                "retry": False,
                "sid": self.sid,
                "bdy": {
                    "msg": message,
                    "msgTypeCode": 1,
                    "extras": json.dumps(extras),
                    "msgTime": int(datetime.now(tz=KST).timestamp()),
                },
            },
        )

    def pong(self) -> None:
        self._send({"ver": "2", "cmd": ChzzkChatCmd.PONG.value})
        if self.chatChannelId != self.api.fetch_chat_channel_id(
            self.streamer_id,
        ):  # 방송 시작시 chatChannelId가 달라지는 문제
            self.connect()

    def run(self) -> Generator[ChzzkChatMessage, None, None]:
        while True:
            raw_message = self._recv()
            chat_cmd = raw_message.get("cmd")

            if chat_cmd == ChzzkChatCmd.PING.value:
                self.pong()
                continue

            if chat_cmd not in (ChzzkChatCmd.CHAT.value, ChzzkChatCmd.DONATION.value):
                continue
            chat_type = ChzzkChatCmd(chat_cmd)

            for chat_data in raw_message.get("bdy", []):
                if "msg" not in chat_data:
                    continue

                if chat_data["uid"] == "anonymous":
                    nickname = "익명의 후원자"
                elif chat_data["uid"] == "SYSTEM_MESSAGE":
                    nickname = "시스템 메시지"
                else:
                    try:
                        profile_data = json.loads(chat_data["profile"])
                        nickname = profile_data["nickname"]
                    except Exception as e:
                        msg = "프로필 데이터 파싱 오류."
                        raise ValueError(msg) from e

                msg_time = datetime.fromtimestamp(chat_data["msgTime"] / 1000, tz=KST)
                if chat_type == ChzzkChatCmd.DONATION:
                    subscribed, donated = False, False
                    payamount = json.loads(chat_data["extras"]).get("payAmount")
                else:
                    profile_data = json.loads(chat_data["profile"])
                    subscribed = bool(
                        profile_data["streamingProperty"].get("subscription", False),
                    )
                    donated = bool(len(profile_data["viewerBadges"]))
                    payamount = None

                yield ChzzkChatMessage(
                    chat_type=chat_type,
                    nickname=nickname,
                    message=chat_data["msg"],
                    timestamp=datetime.strftime(msg_time, "%Y-%m-%d %H:%M:%S"),
                    uid=chat_data["uid"],
                    chat_channel_id=self.chatChannelId,
                    subscribed=subscribed,
                    donated=donated,
                    payamount=payamount,
                )
