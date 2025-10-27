import requests
from bs4 import BeautifulSoup
import datetime
import os
import telegram

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BASE_URL = "https://visitokinawajapan.com/zh-hant/discover/events/"

def get_events_by_month(month: int):
    resp = requests.get(BASE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 最新即時活動區塊
    section = soup.find("h2", string="最新即時活動")
    if not section:
        return []

    events = []
    parent = section.find_next("section")
    if not parent:
        return []

    for dt in parent.find_all("dt"):
        name = dt.text.strip()
        date_div = dt.find_next("div", class_="e-content")
        date_text = date_div.text.strip() if date_div else ""
        # 過濾月份
        try:
            start_date = datetime.datetime.strptime(date_text.split("-")[0].strip(), "%Y/%m/%d")
            if start_date.month == month:
                link_tag = dt.find_previous("a", href=True)
                link = "https://visitokinawajapan.com" + link_tag["href"] if link_tag else BASE_URL
                events.append((date_text, name, link))
        except:
            continue
    return events

def send_telegram(events, month):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if not events:
        msg = f"本月 ({month}月) 沒有找到指定月份的活動。"
    else:
        msg = f"本月 ({month}月) 活動：\n"
        for date_text, name, link in events:
            msg += f"{date_text}\n[{name}]({link})\n"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

if __name__ == "__main__":
    # 從環境變數抓月份，沒設定就抓當月
    month = int(os.environ.get("MONTH", datetime.datetime.now().month))
    events = get_events_by_month(month)
    send_telegram(events, month)
