name: Okinawa Monthly Bot

on:
  schedule:
    - cron: '0 0 0 * * FRI'  # UTC時間，每週五
  workflow_dispatch: # 手動觸發

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install requests beautifulsoup4 lxml
      - name: Run monthly bot
        run: python okiweekly_bot.py
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
