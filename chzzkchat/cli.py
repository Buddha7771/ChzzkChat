import click

from .client import ChzzkApi, ChzzkChatClient
from .constant import CHZZK_VIOLET, CHZZK_VIOLET_DARK, CONFIG_PATH, ChzzkChatCmd


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
@click.option(
    "--streamer",
    "-s",
    type=str,
    required=True,
    help="스트리머의 아이디를 입력하세요.",
)
def connect(streamer: str) -> None:
    client = ChzzkChatClient(streamer_id=streamer)
    for msg in client.run():
        if msg.chat_type == ChzzkChatCmd.DONATION:
            output = click.style(
                f"\n\n {msg.nickname}\n ",
                fg="bright_white",
                bold=True,
                bg=CHZZK_VIOLET_DARK,
            )
            output += click.style(
                f"{msg.message}\n",
                fg="bright_white",
                bg=CHZZK_VIOLET_DARK,
            )
            if msg.payamount is not None:
                output += click.style(
                    f" 🧀 {msg.payamount}\n",
                    fg="bright_white",
                    bold=True,
                    bg=CHZZK_VIOLET_DARK,
                )
            output += "\n"
            click.echo(output)
        elif msg.chat_type == ChzzkChatCmd.CHAT:
            output = []
            if msg.subscribed:
                output.append("💎")
            if msg.donated:
                output.append(click.style("🤍", bg=CHZZK_VIOLET))
            output.append(
                click.style(
                    f"{msg.nickname}",
                    fg=msg.get_rgb_code(),
                    bold=True,
                ),
            )
            output.append(msg.message)
            click.echo(" ".join(output))
