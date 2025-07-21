import telebot
import os
import time
import requests
from datetime import datetime, timedelta, timezone
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

next_draw = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
if datetime.now(timezone.utc) > next_draw:
    next_draw += timedelta(days=2)

def get_binance_price(symbol):
    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
        return float(res.json()["price"])
    except:
        return None

def get_price_info():
    ton_price = get_binance_price("TONUSDT")
    btc_price = get_binance_price("BTCUSDT")
    if ton_price and btc_price:
        return (1 / ton_price), (1 / btc_price)
    return None, None

@bot.message_handler(commands=["start"])
def send_welcome(message):
    ton_amt, btc_amt = get_price_info()
    msg = "🎉 Hoş geldiniz!\n\n"
    msg += "🎟 Bilet Fiyatı: 1 USDT\n"
    if ton_amt and btc_amt:
        msg += f"💎 TON ile: {ton_amt:.2f} TON\n"
        msg += f"₿ BTC ile: {btc_amt:.8f} BTC\n"
    remaining = next_draw - datetime.now(timezone.utc)
    msg += f"\n🕒 Sonraki çekilişe kalan süre: {str(remaining).split('.')[0]}"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=["cekilis"])
def check_draw_time(message):
    remaining = next_draw - datetime.now(timezone.utc)
    bot.send_message(message.chat.id, f"🕒 Sonraki çekilişe kalan süre: {str(remaining).split('.')[0]}")

def draw_loop():
    global next_draw
    while True:
        now = datetime.now(timezone.utc)
        if now >= next_draw:
            print("🎉 Çekiliş zamanı!")
            next_draw += timedelta(days=2)
        time.sleep(10)

threading.Thread(target=draw_loop, daemon=True).start()

print("🤖 Bot çalışıyor...")
bot.polling()
