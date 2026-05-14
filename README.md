# DEV EVENT Discord Bot

사이트의 행사 정보를 자동으로 수집하여 Discord 채널로 전송하는 GitHub Actions 기반 자동화 봇입니다.

## 기능

- DEV EVENT 행사 자동 수집
- Discord Webhook 자동 전송
- GitHub Actions 기반 24시간 자동 실행
- 중복 행사 자동 필터링
- 무료 서버리스 운영 가능
- 5분 단위 자동 모니터링

## 알리미 봇 미리 보기

```
[새로운 개발 행사]
AI 컨퍼런스 2026
https://dev-event.vercel.app/events/xxx
```

## 디렉토리 구조

```
discord-dev-event-bot/
├── bot.py
├── requirements.txt
├── events_cache.json
└── .github/
    └── workflows/
        └── bot.yml
```

## 설치하기

### 1. 레포지토리 복제

```bash
git clone https://github.com/dubu-alt/discord-dev-event-bot
cd discord-dev-event-bot
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

## Discord Webhook 구성 및 설치

1. Discord 채널 설정 진입
2. 연동 → 웹후크(Webhooks)
3. 새 웹후크 생성
4. 웹후크 URL 복사

**예시:**
```
https://discord.com/api/webhooks/xxxxx/xxxxx
```

## GitHub Secrets 설정 방법

GitHub Repository에서:

```
Settings → Secrets and variables → Actions → New repository secret
```

**생성할 시크릿:**

| Name | Value |
|------|-------|
| DISCORD_WEBHOOK_URL | 디스코드 웹훅 URL |

## GitHub Actions Setup

파일 위치: `.github/workflows/bot.yml`

```yaml
name: DEV EVENT BOT

on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest

    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Python Setup
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Packages
        run: |
          pip install -r requirements.txt

      - name: Run Bot
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        run: |
          python bot.py

      - name: Commit cache
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git add events_cache.json
          git diff --cached --quiet || git commit -m "update cache"
          git push
```

## Bot Code (bot.py)

```python
import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
BASE_URL = "https://dev-event.vercel.app/events"
CACHE_FILE = "events_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        sent_events = json.load(f)
else:
    sent_events = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
cards = soup.select("a")

for card in cards:
    text = card.get_text(strip=True)
    href = card.get("href")

    if not href:
        continue

    if "/events/" not in href:
        continue

    full_link = f"https://dev-event.vercel.app{href}"

    if full_link in sent_events:
        continue

    embed = {
        "title": text[:256],
        "url": full_link,
        "description": "새로운 개발 행사",
        "color": 5814783,
        "footer": {
            "text": "DEV EVENT BOT"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    payload = {
        "embeds": [embed]
    }

    requests.post(WEBHOOK_URL, json=payload)
    sent_events.append(full_link)

with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(sent_events, f, ensure_ascii=False, indent=2)
```

## 로컬 실행 방법

```bash
python bot.py
```

## 깃 설치 방법

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## 트러블슈팅 

### 깃 푸쉬 실패

```bash
git pull origin main --allow-unrelated-histories
git add .
git commit -m "merge"
git push -u origin main
```

### GitHub Actions Not Running

- 기본 브랜치가 `main`인지 확인
- Actions 탭에서 활성화 확인
- `workflow_dispatch` 버튼으로 수동 실행 테스트

## 추가 예정

- AI 행사 필터링
- 날짜 파싱
- 마감 임박 알림
- Discord 버튼 UI
- SQLite 저장
- Redis 캐시
- 카테고리별 채널 분리
- 행사 이미지 자동 임베드
- 슬래시 명령어 지원
