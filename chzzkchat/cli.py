import logging
import shutil
from datetime import datetime

import click

from .client import KST, ChzzkApi, ChzzkChatClient
from .constant import (
    CONFIG_PATH,
    ChzzkChatCmd,
    ChzzkColor,
)


@click.group()
def cli() -> None:
    pass


@cli.command()
def login() -> None:
    if CONFIG_PATH.exists():
        click.echo(click.style("⚠️ 이미 로그인된 상태입니다.", fg="yellow"))
        if not click.confirm(
            click.style("기존 쿠키를 덮어쓰시겠습니까?", fg="yellow"),
            default=False,
        ):
            click.echo("로그인을 취소합니다.")
            return

    separator = click.style("-" * 50, fg="green")
    click.echo(separator)
    click.echo(click.style("🔐 네이버 계정 쿠키를 입력하세요.", bold=True))
    click.echo(click.style("- NID_AUT, NID_SES 두 개가 필요합니다."))
    click.echo(separator)

    try:
        ChzzkApi(
            NID_AUT=click.prompt("🔑 NID_AUT", type=str, hide_input=True).strip(),
            NID_SES=click.prompt("🔑 NID_SES", type=str, hide_input=True).strip(),
        ).save()
        click.echo(click.style("✅ 쿠키가 성공적으로 저장되었습니다.", fg="green"))
    except ValueError:
        click.echo(click.style("❌ 오류", fg="red"))
        click.echo(click.style("쿠키 정보를 다시 확인해주세요.", fg="red", bold=True))
    except click.Abort as e:
        click.echo(click.style(f"❌ 입력 오류: {e}", fg="red"))
        click.echo(click.style("다시 시도해주세요.", fg="red", bold=True))


@cli.command()
@click.argument("keyword", type=str, required=True)
@click.option("--log", is_flag=True)
def connect(keyword: str, *, log: bool) -> None:
    streamer_id = ChzzkApi.search_channel_id(keyword)
    client = ChzzkChatClient(streamer_id=streamer_id)
    msg = f"{client.channelName} 채팅 서버에 연결 중..."
    click.echo(msg)
    if log:
        now = datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{client.channelName} {now}.log"
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            format="%(time)s - [%(type)s] - [%(nickname)s] - %(message)s",
            encoding="utf-8",
        )
        logger = logging.getLogger()
        logger.info(
            msg,
            extra={"time": now, "type": "SYSTEM", "nickname": "시스템 메세지"},
        )

    for msg in client.run():
        if msg.chat_type == ChzzkChatCmd.DONATION:
            terminal_width = shutil.get_terminal_size().columns
            if msg.is_system():
                output = click.style(
                    f"\n\n {msg.message}\n",
                    fg="bright_white",
                    bold=True,
                    bg=ChzzkColor.DARK_GRAY.value,
                )
                log_type = "SYSTEM"
            else:
                output = click.style(
                    f"\n\n {msg.nickname}\n",
                    fg="bright_white",
                    bold=True,
                    bg=ChzzkColor.VIOLET_DARK.value,
                )
                output += click.style(
                    f" {msg.message}\n",
                    fg="bright_white",
                    bg=ChzzkColor.VIOLET_DARK.value,
                )
                log_type = "DONATION"
                if msg.payamount is not None:
                    output += click.style(
                        f" 🧀 {msg.payamount}\n",
                        fg="bright_white",
                        bold=True,
                        bg=ChzzkColor.VIOLET_DARK.value,
                    )
            click.echo((output + "\n").ljust(terminal_width))

        elif msg.chat_type == ChzzkChatCmd.CHAT:
            badges = ""
            log_badges = ""
            if msg.subscribed:
                badges += "💎 "
                log_badges += "💎 "
            if msg.donated:
                badges += click.style("🤍", bg=ChzzkColor.VIOLET.value)
                badges += " "
                log_badges += "🤍 "
            nickname = click.style(f"{msg.nickname}", fg=msg.get_rgb_code(), bold=True)
            output = f"{badges}{nickname} {msg.message}"
            click.echo(output)
            log_type = "CHAT"
        else:
            continue

        if log:
            logger.info(
                msg.message,
                extra={
                    "time": msg.timestamp,
                    "type": log_type,
                    "nickname": msg.nickname,
                },
            )
