import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# Telegram 設定（從環境變數讀）
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 目標網站
URL = "https://visitokinawajapan.com/zh-hant/discover/events/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_visit_okinawa_events():
    print("開始抓取 Visit Okinawa Japan 搜尋熱門活動...")
    events = []

    try:
        res = requests.get(URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print("⚠️ 無法連線至網站：", e)
        return events

    soup = BeautifulSoup(res.text, "html.parser")

    # 找到 "搜尋熱門活動" 區塊
    section = soup.find("h2", string="搜尋熱門活動")
    if not section:
        print("⚠️ 找不到『搜尋熱門活動』區塊。")
        return events

    container = section.find_next("div")
    if not container:
        print("⚠️ 找不到活動列表。")
        return events

    # 計算當月 + 未來兩個月的月份列表
    today = datetime.now()
    months_to_include = [(today + timedelta(days=30*i)).month for i in range(3)]

    # 找出每個活動區塊
    for item in container.find_all("a", href=True):
        name_tag = item.find("dt")
        date_tag = item.find("div", class_="e-content")
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True).rstrip(")")
        date_text = date_tag.get_text(strip=True) if date_tag else ""
        link = item["href"]
        if not link.startswith("http"):
            link = "https://visitokinawajapan.com" + link

        # 判斷活動開始月份是否在當月 + 未來兩個月
        if date_text and "-" in date_text:
            try:
                start_date_str = date_text.split("-")[0].strip()
                start_dt = datetime.strptime(start_date_str, "%Y/%m/%d")
                if start_dt.month in months_to_include:
                    events.append({"name": name, "date": date_text, "url": link})
            except Exception:
                continue

    # 按開始日期排序
    events.sort(key=lambda x: x['date'])
    print(f"✅ 共找到 {len(events)} 個活動 (當月+未來兩個月)")
    return events

def send_to_telegram(events):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ 未設定 TELEGRAM_TOKEN 或 CHAT_ID，略過發送。")
        return

    message = "📅 沖繩熱門活動 (當月 + 未來兩個月)\n\n"
    for e in events:
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
    events = get_visit_okinawa_events()
    send_to_telegram(events)
