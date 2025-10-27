import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BASE_URL = "https://visitokinawajapan.com/zh-hant/discover/events/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_events():
    events = []
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print("⚠️ 無法連線至網站：", e)
        return events

    soup = BeautifulSoup(res.text, "lxml")
    
    # 抓全部活動
    for dt in soup.find_all("dt"):
        name = dt.get_text(strip=True)
        # 對應日期
        date_div = dt.find_next("div", class_="e-content")
        date_text = date_div.get_text(strip=True) if date_div else ""
        # 超連結
        link_tag = dt.find_parent("a", href=True)
        link = "https://visitokinawajapan.com" + link_tag["href"] if link_tag else BASE_URL
        # 過濾當月 + 後兩個月
        try:
            start_date_str = date_text.split("-")[0].strip()
            start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
            now = datetime.now()
            upper_limit = now + timedelta(days=90)
            if now <= start_date <= upper_limit:
                events.append({"date": date_text, "name": name, "url": link})
        except Exception:
            continue
    # 按日期排序
    events.sort(key=lambda x: x["date"])
    return events

def send_to_telegram(events):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ 未設定 TELEGRAM_TOKEN 或 CHAT_ID")
        return
    if not events:
        message = "📅 沖繩熱門活動 (當月 + 未來兩個月)\n目前沒有活動資訊。"
    else:
        message = "📅 沖繩熱門活動 (當月 + 未來兩個月)\n\n"
        for e in events:
            message += f"{e['date']}\n[{e['name']}]({e['url']})\n"
    try:
        import telegram
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print("Telegram 發送成功 ✅")
    except Exception as e:
        print("Telegram 發送失敗：", e)

if __name__ == "__main__":
    events = get_events()
    send_to_telegram(events)
