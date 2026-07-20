"""
Разовая проверка спреда BTC/ETH за 24ч. Предназначен для запуска по расписанию
(GitHub Actions), а не в бесконечном цикле.

TELEGRAM_TOKEN и CHAT_ID берутся из переменных окружения (задаются как GitHub Secrets),
токен нигде не хранится в самом коде.
"""

import os
import requests

THRESHOLD = 2.0  # порог разницы в % (можно 2.0-3.0)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BINANCE_URL = "https://data-api.binance.vision/api/v3/ticker/24hr"


def get_24h_change(symbol: str) -> float:
    resp = requests.get(BINANCE_URL, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    return float(resp.json()["priceChangePercent"])


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)


def describe_scenario(btc_change: float, eth_change: float) -> str:
    if btc_change >= 0 and eth_change >= 0:
        leader = "ETH" if eth_change > btc_change else "BTC"
        return f"Рынок растёт, но {leader} растёт сильнее"
    if btc_change <= 0 and eth_change <= 0:
        leader = "ETH" if eth_change < btc_change else "BTC"
        return f"Рынок падает, но {leader} падает сильнее"
    return "Разнонаправленное движение (один растёт, другой падает)"


def main():
    btc_change = get_24h_change("BTCUSDT")
    eth_change = get_24h_change("ETHUSDT")
    diff = eth_change - btc_change

    print(f"BTC 24h: {btc_change:+.2f}%  |  ETH 24h: {eth_change:+.2f}%  |  разница: {diff:+.2f}%")

    if abs(diff) >= THRESHOLD:
        scenario = describe_scenario(btc_change, eth_change)
        text = (
            f"⚠️ Спред BTC/ETH за 24ч: {abs(diff):.2f}%\n\n"
            f"BTC: {btc_change:+.2f}%\n"
            f"ETH: {eth_change:+.2f}%\n\n"
            f"Сценарий: {scenario}"
        )
        send_telegram_message(text)
        print("-> Уведомление отправлено")


if __name__ == "__main__":
    main()
