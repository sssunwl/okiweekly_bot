import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# Telegram 設定
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 網站 URL
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

    # 找所有 <dt> 活動名稱
    dt_tags = soup.find_all("dt")
    today = datetime.now()
    months_to_include = [(today + timedelta(days=30*i)).month for i in range(3)]  # 當月 + 未來兩個月

    for dt in dt_tags:
        name = dt.get_text(strip=True).rstrip(")")
        date_div = dt.find_next("div", class_="e-content")
        date_text = date_div.get_text(strip=True) if date_div else ""
        link_tag = dt.find_parent("a", href=True)
        link = "https://visitokinawajapan.com" + link_tag["href"] if link_tag else URL

        if date_text and "-" in date_text:
            try:
                start_date_str = date_text.split("-")[0].strip()
                start_dt = datetime.strptime(start_date_str, "%Y/%m/%d")
                if start_dt.month in months_to_include:
                    events.append({"name": name, "date": date_text, "url": link})
            except:
                continue

    # 依日期排序
    events.sort(key=lambda x: x['date'])
    print(f"✅ 共找到 {len(events)} 個活動 (當月+未來兩個月)")
    return events

def send_to_telegram(events):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ 未設定 TELEGRAM_TOKEN 或 CHAT_ID，略過發送。")
        return

    if not events:
        message = "本週沒有新的活動。"
    else:
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
