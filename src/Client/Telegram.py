import os
import telebot
import requests
import json
import urllib.parse
import asyncio
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="/Users/xinchangyi/Desktop/fengshuiagents_dev/src/.env")

bot = telebot.TeleBot(os.getenv("Telegram_API_KEY"))
print("telebot env key: ", os.getenv("Telegram_API_KEY"))

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    aisay = requests.post('http://localhost:8000/chat?query=Hello Yinseer Chen!')
    aisay = json.loads(aisay.text)
    print(aisay)
    text_without_quotes = aisay["msg"]["output"].strip('"')
    bot.reply_to(message, text_without_quotes.encode('utf-8'))

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    try:
        encoded_text = urllib.parse.quote(message.text)
        aisay_response = requests.post('http://localhost:8000/chat?query=' + encoded_text, timeout=100)
        if aisay_response.status_code == 200:
            aisay = json.loads(aisay_response.text)
            if "msg" in aisay:
                bot.reply_to(message, aisay["msg"]["output"].encode('utf-8'))
                
            else:
                bot.reply_to(message, "server error!")
        else:
            bot.reply_to(message, "server error!")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        bot.reply_to(message, "Sorry, Master is tired!")

async def check_audio(message, audio_file):
    while True:
        if os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
            os.remove(audio_file)
            break
        else:
            print("waiting for audio file...")
            await asyncio.sleep(1)


bot.infinity_polling()