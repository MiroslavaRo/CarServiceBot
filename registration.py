"""User registration"""
import sqlite3
import re
import logging
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import credentials
import design
import contacts
import models

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Bot instance
bot = credentials.bot

con = sqlite3.connect("supercar.db")
cursor = con.cursor()

user_dict = models.user_dict

def part_registration(call):
    """Returns buttons for choosing what part of info user would like to change"""
    button_list = [
        InlineKeyboardButton("Personal", callback_data='reg'),
        InlineKeyboardButton("Car", callback_data='change_car')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=2))
    cid = call.from_user.id
    text="What part would you like to change in your profile?"
    bot.send_message(cid, text,  reply_markup = reply_markup)

# ----REGISTRATION CONTACT-----

@bot.edited_channel_post_handler(func=lambda call: True)
def registration(call):
    """Starts registration and asks user to enter their name"""
    cid = call.from_user.id
    mid = call.message.message_id
    logger.warning('%d + %d + %s' %(cid, mid, call.message.text))
    text = 'Starting registration proces...\n\nEnter your full name'

    msg = bot.send_message(cid, text, reply_markup = design.keyboard())
    bot.register_next_step_handler(msg, process_name_step)


def phone():
    """Returns button to send phone number automaticly"""
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    button_phone = types.KeyboardButton(text = "Send phone", request_contact = True)
    keyboard.add(button_phone)
    return keyboard


@bot.message_handler(func=lambda message: message.text in design.menu_hello_options)
def check_bttns(message):
    """Checks if user entered commands and keywords"""
    logger.warning("IN ARRAY")
    design.handle_menu_click(message)


def process_name_step(message):
    """Continues registration, gets user name and then asks user to enter their phone number"""
    logger.warning(message.text)

    name_regrex = '[A-Za-z]{2,25}( [A-Za-z]{1,25})?'
    try:
        chat_id = message.chat.id
        name = message.text
        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)

        elif bool(re.fullmatch(name_regrex, name)):
            user = models.User(name)
            user_dict[chat_id] = user
            msg = bot.reply_to(message,
'Enter your phone number\n(Or select the current one from the keyboard)', reply_markup = phone())
            bot.register_next_step_handler(msg, process_phone_step)
        else:
            msg = bot.reply_to(message,
'''Name cannot contain special characters, numbers and be less then 1 letter.\n
Please try again. Enter your full name''')
            bot.register_next_step_handler(msg, process_name_step)

    except Exception as exc:
        logger.error(exc)
        bot.reply_to(message, 'Something went wrong')
        contacts.contacts_msg(message)


@bot.message_handler(content_types = ['contact'])
def process_phone_step(message):
    """Continues registration, gets user phone number and then asks user to enter their email"""
    logger.warning(message.text)

    phonereg = '^\\+?[1-9][0-9]{7,14}$'
    try:
        chat_id = message.chat.id
        phone_var = message.text

        if(phone_var is None)  | (message.contact is not None):
            phone_var = message.contact.phone_number
            logger.warning(phone_var)
        if bool(re.fullmatch(phonereg, phone_var)):
            user = user_dict[chat_id]
            user.phone = phone_var
            msg = bot.send_message(chat_id,
'Enter your email\n(Write "-" to skip the step)', reply_markup = design.keyboard())
            bot.register_next_step_handler(msg, process_email_step)
        else:
            msg = bot.reply_to(message,
'Please write your phone number in international format(For example: +12223334444)')
            bot.register_next_step_handler(msg, process_phone_step)
    except Exception as exc:
        logger.error(exc)
        bot.reply_to(message, 'Something went wrong')
        contacts.contacts_msg(message)

def reg_contact_buttons():
    """Returns buttons to confirm registration"""
    button_list = [
        InlineKeyboardButton("Yes", callback_data='save_user'),
        InlineKeyboardButton("No", callback_data='cancel_user')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=2))
    return reply_markup


@bot.edited_channel_post_handler(func=lambda call: True)
def process_email_step(message):
    """Continues registration, gets user email and then asks user to confirm registration"""
    logger.warning(message.text)
    emailreg = '([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    try:
        chat_id = message.chat.id
        email = message.text

        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)
        elif(message.text == '-') | (bool(re.fullmatch(emailreg, email))):
            user = user_dict[chat_id]
            user.email = email
            info = f'''<b>Your contact information:</b>\n
👤{user_dict[chat_id].name}
📞Tel.:{user_dict[chat_id].phone}
📧 Email: {user_dict[chat_id].email}
\n\n<b>Save changes?</b>'''
            bot.send_message(chat_id, info, parse_mode='html', reply_markup= reg_contact_buttons())
        else:
            msg = bot.reply_to(message,
'Please enter valid email address or write "-" to skip the step')
            bot.register_next_step_handler(msg, process_email_step)
    except Exception as exc:
        logger.error(exc)
        bot.reply_to(message, 'Something went wrong')
        contacts.contacts_msg(message)
