from enum import Enum
from pathlib import Path


class ChzzkChatCmd(Enum):
    PING = 0
    PONG = 10000
    CONNECT = 100
    SEND_CHAT = 3101
    REQUEST_RECENT_CHAT = 5101
    CHAT = 93101
    DONATION = 93102


class ChzzkColor(Enum):
    VIOLET = (111, 65, 227)
    VIOLET_DARK = (88, 79, 162)
    DARK_GRAY = (20, 21, 23)


CONFIG_PATH = Path.home() / ".config" / "chzzkchat" / "config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "",
    "Connection": "close",
}


# fmt: off
NICKNAME_PALLETTE = [
    "#EEA05D", "#EAA35F", "#E98158", "#E97F58",
    "#E76D53", "#E66D5F", "#E16490", "#E481AE",
    "#E481AE", "#D25FAC", "#D263AE", "#D66CB4",
    "#D071B6", "#AF71B5", "#A96BB2", "#905FAA",
    "#B38BC2", "#9D78B8", "#8D7AB8", "#7F68AE",
    "#9F99C8", "#717DC6", "#7E8BC2", "#5A90C0",
    "#628DCC", "#81A1CA", "#ADD2DE", "#83C5D6",
    "#8BC8CB", "#91CBC6", "#83C3BB", "#7DBFB2",
    "#AAD6C2", "#84C194", "#92C896", "#94C994",
    "#9FCE8E", "#A6D293", "#ABD373", "#BFDE73",
]
# fmt: on
