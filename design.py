"""Design buttons,  keywords and comapny information"""
import logging
from telebot import types
from telebot.types import InlineKeyboardMarkup,  InlineKeyboardButton
import contacts
import credentials
import services
import texts

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Bot instance
bot = credentials.bot

#Key words
start_commands= ["/start","/help", "/home"]
other_commands = ['/profile','/aboutus','/services','/question']
menu_options = ['🚘 services','home', '🌎 about us','👩‍🏫 profile']
menu_hello_options = ['home','hi','hello','start','help','menu','back','go']
menu_ask_options = ['question','questions','ask','suggestion','manager','human','chat with manager','chat with human']
menu_products = ['products','product','service','services']
menu_price_services = ['price', 'prices','cost'] +menu_products

key_diagnostics = ['diagnostics','diagnostics', 'undercarriage','computer','check']
key_maintenance = ['maintenance','comprehensive']
key_conditioner = ['conditioner', 'refuele','refueling']#,'refueling conditioner'
key_paint = ['painting','paint','tuning','scaffold','scaffolding','polish','polishing']
key_repair = ['repair','fix','damage']

service_names = key_diagnostics+key_maintenance+key_conditioner+key_paint+key_repair

all_keywords = start_commands + other_commands + menu_options + menu_hello_options + menu_ask_options
all_keywords += menu_price_services + service_names #+ services.services_btns

# ----------BUTTONS LAYOUT DESIGN----------
def build_menu(buttons,  n_cols,  header_buttons = None,  footer_buttons = None):
    """Helper function for building a list of buttons in a grid"""
    menu = [buttons[i: i + n_cols] for i in range(0,  len(buttons),  n_cols)]
    if header_buttons:
        menu.insert(0,  header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

# --------------KEYBOARD MENU--------------
def keyboard():
    """Defines keyboard options and returns buttons"""
    menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
    btn0 = types.KeyboardButton("Home")
    btn1 = types.KeyboardButton("🚘 services")
    btn2 = types.KeyboardButton("🌎 about us")
    btn3 = types.KeyboardButton("👩‍🏫 profile")
    menu_keyboard.add(btn1, btn2, btn3).add(btn0)
    return menu_keyboard


@bot.message_handler(func = lambda message:  message.text.lower() in menu_options)
@bot.message_handler(func = lambda message: message.text.lower() == "profile")
@bot.message_handler(func = lambda message: message.text.lower() in menu_hello_options)
def handle_menu_click(message):
    """Displays menu-message that allows to choose operation"""
    if (message.text.lower() == "home") | (message.text.lower() in menu_hello_options):
        photo = open('./imgs/welcome.jpg',  'rb')
        bot.send_photo(message.from_user.id,  photo, texts.WELCOME_TEXT, parse_mode = 'html',
reply_markup = welcome_message_with_buttons())
        bot.send_message(message.from_user.id, texts.KEYBOARD, parse_mode = 'html',
reply_markup = keyboard())
    elif message.text.lower() == "🌎 about us":
        company_info(message)
    elif (message.text.lower() == '👩‍🏫 profile') | (message.text == "profile"):
        contacts.contacts_msg(message)
    elif message.text.lower() == '🚘 services':
        services.price_msg(message)
        bot.send_message(message.from_user.id, "Services options 👇",
reply_markup = services.keyboard_services())

# -----------------WELCOME BTNS---------
def welcome_message_with_buttons():
    """Returns message buttons to choose operation"""
    button_list = [
        InlineKeyboardButton("Our contacts",  callback_data = 'contacts'), 
        InlineKeyboardButton("Services and Products",  callback_data = 'sap'), 
        InlineKeyboardButton("Your profile",  callback_data = 'profile')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,  n_cols = 1))
    return reply_markup

# ------------------1. COMPANY INFO---------------------------
@bot.message_handler(commands = ["aboutus"])
def company_info(message):
    """Returns message button to visit website"""
    button_list = [
        InlineKeyboardButton("🌐 Our website",  url = 'https://facebook.com')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list,  n_cols = 1))
    bot.send_message(message.from_user.id, texts.COMPANY_INFO, parse_mode = 'html', 
reply_markup = reply_markup)

def remove_last_bot_message_buttons():
    """Allows to remove message buttons on last bot message"""
    msg = credentials.last_bot_message
    if msg is None:
        return
    bot.edit_message_text(msg.text,  msg.chat.id,  msg.message_id)
