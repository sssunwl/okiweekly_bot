import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib.parse

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BASE_URL = "https://visitokinawajapan.com/zh-hant/discover/events/"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram token or chat_id not set")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        print("Telegram 發送成功 ✅")
    except Exception as e:
        print("Telegram 發送失敗：", e)

def parse_events():
    resp = requests.get(BASE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 當前月 + 下個月
    today = datetime.today()
    months_to_check = [today.month, (today + timedelta(days=31)).month]

    events_section = soup.find("section", {"class": "c-event-latest"})  # 最新即時活動
    if not events_section:
        return []

    events = []
    for dt_tag in events_section.find_all("dt"):
        name = dt_tag.get_text(strip=True)
        dd_tag = dt_tag.find_next_sibling("div", {"class": "e-content"})
        date_text = dd_tag.get_text(strip=True) if dd_tag else ""
        # 解析開始月
        start_month = None
        if "-" in date_text:
            start_str = date_text.split("-")[0].strip()
            try:
                start_date = datetime.strptime(start_str, "%Y/%m/%d")
                start_month = start_date.month
            except:
                start_month = None
        # 只抓當月或下個月
        if start_month and start_month in months_to_check:
            link_tag = dt_tag.find_previous("a", href=True)
            link = urllib.parse.urljoin(BASE_URL, link_tag['href']) if link_tag else BASE_URL
            events.append(f"{date_text}\n<a href='{link}'>{name}</a>")
    return events

def main():
    try:
        events = parse_events()
        if not events:
            send_telegram(f"本週沒有找到指定月份的活動。")
        else:
            message = "\n".join(events)
            send_telegram(message)
    except Exception as e:
        print("抓取發生錯誤：", e)

if __name__ == "__main__":
    main()
