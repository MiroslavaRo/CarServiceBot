import telebot
import os
from dotenv import load_dotenv

load_dotenv('.env')

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = "https://t.me/super_car_service_bot"
bot = telebot.TeleBot(BOT_TOKEN)

MAX_CARS = 10
last_bot_message = None
