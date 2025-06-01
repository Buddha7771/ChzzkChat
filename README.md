<div align="center">

# ChzzkChat

**ChzzkChat**은 파이썬과 터미널에서 치지직 채팅창에 간편하게 연결할 수 있는 라이브러리입니다.

</div>


## 📦 설치

pip를 사용해 간편하게 설치할 수 있습니다.

```bash
pip install chzzkchat
```

> [!Warning]
> python 3.10 이상이 필요합니다.


## 🔐 로그인
채팅에 연결하려면 네이버 쿠키 정보가 필요합니다. 아래 과정을 통해 쿠키를 등록해주세요.

1. 웹 브라우저에서 네이버에 로그인합니다.
2. 개발자 도구(F12)를 열어 쿠키 탭에서 `NID_AUT`, `NID_SES` 값을 찾아 복사합니다.
3. 아래 명령어로 쿠키를 등록합니다.

```bash
chzzkchat login
```


## 🚀 사용 방법

### ✅ 터미널에서 사용하기
아래 명령어를 사용해 터머널에서 특정 스트리머의 채팅창에 연결할 수 있습니다. (입력한 키워드와 일치하는 채널 중 검색 결과 최상단 채널로 접속합니다.)

```bash
chzzkchat connect 녹두로
```

> [!Note]
> `--log` 옵션을 추가하면 채팅 로그가 현재 디렉토리에 저장됩니다.
> (예: `chzzkchat connect 녹두로 --log`)


### ✅ 파이썬 코드에서 사용하기
파이썬 코드 내에서 실시간 채팅을 수집하려면 다음 예제를 참고하세요.

```python
from chzzkchat import ChzzkApi, ChzzkChatClient

# 스트리머 이름으로 채널 ID 검색
keyword = "녹두로"
streamer_id = ChzzkApi.search_channel_id(keyword)

# 채팅 클라이언트 실행
client = ChzzkChatClient(streamer_id=streamer_id)

# 실시간 채팅 출력
for msg in client.run():
    output = f"[{msg.timestamp}] "
    output += f"[{msg.chat_type.name}] "
    output += f"{msg.nickname}: {msg.message}"
    print(output)
```