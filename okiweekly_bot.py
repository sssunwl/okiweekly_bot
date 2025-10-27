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

    section = soup.find("h2", string="最新即時活動")
    if not section:
        return []

    events = []
    parent = section.find_next("section")
    if not parent:
        return []

    for dt in parent.find_all("dt"):
        name = dt.text.strip().strip(" )")  # 清掉多餘括號和空格
        date_div = dt.find_next("div", class_="e-content")
        date_text = date_div.text.strip() if date_div else ""
        try:
            start_date_str = date_text.split("-")[0].strip()
            start_date = datetime.datetime.strptime(start_date_str, "%Y/%m/%d")
            if start_date.month == month:
                # 找到對應的超連結
                link_tag = dt.find_previous("a", href=True)
                link = "https://visitokinawajapan.com" + link_tag["href"] if link_tag else BASE_URL
                events.append((start_date, date_text, name, link))
        except:
            continue

    # 按開始日期排序
    events.sort(key=lambda x: x[0])
    return events

def send_telegram(events_dict):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    msg = ""
    for month, events in events_dict.items():
        if not events:
            msg += f"{month}月沒有找到活動。\n\n"
        else:
            msg += f"{month}月活動：\n"
            for _, date_text, name, link in events:
                msg += f"{date_text}\n[{name}]({link})\n"
            msg += "\n"
    bot.send_message(chat_id=CHAT_ID, text=msg.strip(), parse_mode="Markdown")

if __name__ == "__main__":
    now = datetime.datetime.now()
    this_month = now.month
    next_month = (now.replace(day=28) + datetime.timedelta(days=4)).month  # 下個月
    months = [this_month, next_month]

    events_dict = {}
    for m in months:
        events_dict[m] = get_events_by_month(m)

    send_telegram(events_dict)
