import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# Telegram 設定（從環境變數讀）
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 目標網站
BASE_URL = "https://visitokinawajapan.com/zh-hant/discover/events/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_events_next_two_months():
    events = []

    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print("⚠️ 無法連線至網站：", e)
        return events

    soup = BeautifulSoup(res.text, "html.parser")

    # 找到「搜尋熱門活動」區塊
    section = soup.find("h2", string="搜尋熱門活動")
    if not section:
        print("⚠️ 找不到『搜尋熱門活動』區塊。")
        return events

    container = section.find_next("section")  # 包含活動列表的父層
    if not container:
        print("⚠️ 找不到活動列表容器。")
        return events

    now = datetime.now()
    month_limit = [(now.month + i -1) % 12 +1 for i in range(3)]  # 當月 + 未來兩個月

    for item in container.find_all("a", href=True):
        name_tag = item.find("dt")
        date_tag = item.find("div", class_="e-content")

        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)
        date_text = date_tag.get_text(strip=True) if date_tag else ""

        # 超連結
        link = item["href"]
        if not link.startswith("http"):
            link = "https://visitokinawajapan.com" + link

        # 過濾當月 + 未來兩個月
        if date_text and "-" in date_text:
            try:
                start_date = datetime.strptime(date_text.split("-")[0].strip(), "%Y/%m/%d")
                if start_date.month in month_limit:
                    events.append({"name": name, "date": date_text, "url": link})
            except:
                continue

    print(f"✅ 共找到 {len(events)} 個活動")
    return events

def send_to_telegram(events):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ 未設定 TELEGRAM_TOKEN 或 CHAT_ID，略過發送。")
        return

    message = "📅 沖繩熱門活動 (當月 + 未來兩個月)\n\n"
    if not events:
        message += "目前沒有活動資訊。"
    else:
        for e in events:
            # Markdown 超連結格式
            message += f"{e['date']}\n[{e['name']}]({e['url']})\n"

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        resp = requests.post(send_url, data=data)
        resp.raise_for_status()
        print("Telegram 發送成功 ✅")
    except Exception as e:
        print("Telegram 發送失敗：", e)

if __name__ == "__main__":
    events = get_events_next_two_months()
    send_to_telegram(events)
