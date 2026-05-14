import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

BASE_URL = "https://dev-event.vercel.app/events"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(BASE_URL, headers=headers)

if response.status_code != 200:
    print("사이트 요청 실패")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

cards = soup.select("a")

sent = set()

for card in cards:

    text = card.get_text(strip=True)
    href = card.get("href")

    if not href:
        continue

    if "/events/" not in href:
        continue

    full_link = f"https://dev-event.vercel.app{href}"

    if full_link in sent:
        continue

    sent.add(full_link)

    if len(text) < 5:
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

    r = requests.post(WEBHOOK_URL, json=payload)

    print(text, r.status_code)