"""Registration cars"""
from datetime import date
import re
import logging
from telebot import types
from telebot.types import InlineKeyboardMarkup,  InlineKeyboardButton
import appointments
import credentials
import design
import contacts
import models

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Bot instance
bot = credentials.bot

car_dict = models.car_dict
MAX_CARS = credentials.MAX_CARS

change_car_options = []
change_car = 'change'  # change | delete | choose

# -------------REGISTRATION CAR--------------------

def car_reg_buttons():
    """Buttons for registration"""
    button_list = [
        InlineKeyboardButton("Manually",  callback_data ='manually'),
        InlineKeyboardButton("Photo of tech passport",  callback_data='tech_pass')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list,  n_cols=2))
    return reply_markup

def car_registration(msg):
    """Start registration"""
    cid = msg.chat.id
    mid = msg.message_id
    logger.warning(f"{cid} + {mid} + {msg.text}")
    text = "Starting registration proces..."
    new_text = "How would you like to register your car?"

    bot.send_message(cid, text, reply_markup = design.keyboard())
    bot.send_message(cid, new_text, reply_markup = car_reg_buttons())

def carlist_buttons(cid):
    """Returns cars in keyboard"""
    user = contacts.user_info(cid)
    menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)

    if user is None:
        text = "You are not registred yet.\nSign in?"
        bot.send_message(cid, text, reply_markup = contacts.register_butn())
        return menu_keyboard

    carlist = user['carlist']
    if carlist is None:
        return menu_keyboard

    cars = []
    change_car_options.clear()
    for index,  car in enumerate(carlist):
        brand = car['brand']
        model = car['model']
        year = car['year']
        engine = car['engine']
        if(brand is None) | (model is None) | (year is None):
            car_txt = f"{index+1}. Your tech passport processing."
        else:
            car_txt = f"{index+1}. {brand} {model} {year}({engine})"

        cars.append(car_txt)
        change_car_options.append(car_txt)

    for car in cars:
        menu_keyboard.add(types.KeyboardButton(text = car))

    return menu_keyboard

def  change_car_buttons(cid):
    """Add cars and Add/Delete option in keyboard"""
    menu_keyboard = carlist_buttons(cid)

    change_car_options.append('Add car')

    if contacts.user_info(cid)['carlist'] is None:
        menu_keyboard.add(types.KeyboardButton(text = "Add car"))
    elif len(contacts.user_info(cid)['carlist']) == 0:
        menu_keyboard.add(types.KeyboardButton(text = "Add car"))
    else:
        menu_keyboard.add(types.KeyboardButton(text = "Add car"),  types.KeyboardButton(text = "Delete car"))
        change_car_options.append('Delete car')

    menu_keyboard.add(types.KeyboardButton(text = "Home"))

    return menu_keyboard

def car_change(call):
    """Change option"""
    cid = call.from_user.id
    global change_car
    change_car = 'change'
    bot.send_message(cid, 'Choose car to change', reply_markup = change_car_buttons(cid))

def delete_car_buttons(cid):
    """Delete option chosen"""
    menu_keyboard = carlist_buttons(cid)
    return menu_keyboard

def car_delete_choose(msg):
    """Car for removal"""
    cid = msg.chat.id
    bot.send_message(cid, 'Choose car to delete', reply_markup = carlist_buttons(cid))

def delete_car_buttons():
    """Confirmation buttons"""
    button_list =  [
        InlineKeyboardButton("Yes",  callback_data = 'delete_car'), 
        InlineKeyboardButton("No",  callback_data = 'cancel_delete')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list,  n_cols=2))
    return reply_markup

def car_delete_next_step(msg):
    """Deletion confirmation"""
    cid = msg.chat.id
    bot.send_message(cid, 'Are you sure you want to delete this car from your profile:', reply_markup = design.keyboard())
    car_dict[cid] = models.Car(cid)
    car_dict[cid].car_id = cid*MAX_CARS+int(msg.text[0])-1
    bot.send_message(cid, f'{msg.text}', reply_markup= delete_car_buttons())

@bot.message_handler(func=lambda message: message.text in change_car_options)
def handle_menu_changeinfo_car(message):
    """Options change/choose/delete car pressed"""
    global change_car
    cid = message.chat.id
    for option in change_car_options:
        if message.text != option:
            continue

        if option == 'Add car':
            car = models.Car(cid)
            if contacts.user_info(cid)['carlist'] is None:
                car_index = 0
            else:
                car_index = len(contacts.user_info(cid)['carlist'])
            car.car_id = cid*MAX_CARS+car_index
            car_dict[cid] = car
            logger.warning(f"Add car. car_id: {car_dict[cid].car_id},  car_index: {car_index}")
            car_registration(message)

        elif option == 'Delete car':
            change_car = 'delete'
            car_delete_choose(message)

        elif change_car == 'change':
            car_id = cid*MAX_CARS+int(option[0])-1
            car = models.Car(cid)
            car.car_id = car_id
            car_dict[cid] = car
            logger.warning("change car", car_dict[cid].car_id)
            car_registration(message)

        elif change_car == 'choose':
            car_id = cid*MAX_CARS+int(option[0])-1
            car = models.Car(cid)
            car.car_id = car_id
            car_dict[cid] = car
            logger.warning("choose car", car_dict[cid].car_id)
            appointments.car_for_app(message, car.car_id)

        elif change_car == 'delete':
            car_delete_next_step(message)

        else:
            pass

        return

# -----Tech Passport-------

def tech_pass_step(call):
    """Ask for technical passport"""
    cid = call.from_user.id
    new_text = "Please send photo of a technical passport"
    msg = bot.send_message(cid,  new_text)
    bot.register_next_step_handler(msg,  process_tech_pass_step)

def reg_techpass_buttons():
    """Save tech passport buttons"""
    button_list = [
        InlineKeyboardButton("Yes",  callback_data='save_techpass'),
        InlineKeyboardButton("No",  callback_data='cancel_techpass')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list,  n_cols=2))
    return reply_markup

def process_tech_pass_step(message):
    """Process tech passport""" 
    chat_id = message.chat.id

    try:
        file_path = bot.get_file(message.photo[0].file_id).file_path
        file = bot.download_file(file_path)

        car_dict[chat_id].tech_passport = file

        info = 'Your technical passport processing.\nSave changes?'
        logger.warning(info)
        credentials.last_bot_message = bot.reply_to(message, info, reply_markup = reg_techpass_buttons())

    except Exception as e:
        logger.error(e)
        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)
        else:
            msg = bot.reply_to(message, 'Please send photo of a technical passport')
            bot.register_next_step_handler(msg,  process_tech_pass_step)

# ----------Manually-------------

def reg_car_buttons():
    """Register buttons"""
    button_list = [
        InlineKeyboardButton("Yes",  callback_data='save_car'),
        InlineKeyboardButton("No",  callback_data='cancel_car')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list,  n_cols=2))
    return reply_markup

@bot.message_handler(content_types = ['manually'])
def manual_reg_step(call):
    """Manually option"""
    cid = call.from_user.id

    new_text = "Enter brand of your car"
    msg = bot.send_message(cid,  new_text)
    bot.register_next_step_handler(msg,  process_brand_step)

def process_brand_step(message):
    """Process brand"""
    logger.warning(message.text)

    brand_regrex = '.{3,25}'
    try:
        chat_id = message.chat.id
        brand = message.text

        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)

        elif bool(re.fullmatch(brand_regrex,  brand)):
            car = car_dict[chat_id]
            car.brand = brand
            msg = bot.reply_to(message,  'Enter model of your car')
            bot.register_next_step_handler(msg,  process_model_step)
        else:
            msg = bot.reply_to(message,  'Brand cannot be less then 2 letters.\n\nPlease try again. Enter brand of your car')
            bot.register_next_step_handler(msg,  process_brand_step)

    except Exception as e:
        logger.error(e)
        bot.reply_to(message,  'Something went wrong')
        contacts.contacts_msg(message)

def process_model_step(message):
    """Process model"""
    logger.warning(message.text)

    model_regrex = '.{3,50}'
    try:
        chat_id = message.chat.id
        model = message.text
        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)

        elif bool(re.fullmatch(model_regrex,  model)):
            car = car_dict[chat_id]
            car.model = model
            msg = bot.reply_to(message,  'Enter a year of your car')
            bot.register_next_step_handler(msg,  process_year_step)
        else:
            msg = bot.reply_to(message,  'Model cannot be less then 2 letters.\n\nPlease try again. Enter model of your car')
            bot.register_next_step_handler(msg,  process_model_step)

    except Exception as e:
        logger.error(e)
        bot.reply_to(message,  'Something went wrong')
        contacts.contacts_msg(message)


def process_year_step(message):
    """Process year"""
    logger.warning(message.text)

    min_year = 1960
    try:
        chat_id = message.chat.id
        year = 0
        if message.text.isdigit():
            year = int(message.text)

        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)

        elif year <= int(date.today().strftime("%Y")) and year >= min_year:
            car = car_dict[chat_id]
            car.year = year
            msg = bot.reply_to(message,  'Enter engine of your car\n(Write "-" to skip the step)')
            bot.register_next_step_handler(msg,  process_engine_step)
        else:
            msg = bot.reply_to(message,  f'Year must be a number from 1960 to {date.today().strftime("%Y")}.\n\nPlease try again. Enter a year of your car')
            bot.register_next_step_handler(msg,  process_year_step)

    except Exception as e:
        logger.error(e)
        bot.reply_to(message,  'Something went wrong')
        contacts.contacts_msg(message)

def process_engine_step(message):
    """Process engine"""
    logger.warning(message.text)

    engine_regrex = '.{3,25}'
    try:
        chat_id = message.chat.id
        engine = message.text

        if message.text.lower() in design.all_keywords:
            design.handle_menu_click(message)

        elif(engine == '-') | bool(re.fullmatch(engine_regrex,  engine)):
            car = car_dict[chat_id]
            car.engine = engine
            info = f'<b>🚖Your car info:</b>\n\nBrand: {car_dict[chat_id].brand}\nModel: {car_dict[chat_id].model}\nYear: {car_dict[chat_id].year}\nEngine: {car_dict[chat_id].engine}'
            logger.warning(info)
            text = info+ "\n\n<b>Save changes?</b>"
            bot.send_message(chat_id, text, parse_mode='html', reply_markup = reg_car_buttons())
        else:
            msg = bot.reply_to(message, 'Engine must be more then 2 characters.\n\nPlease try again. Enter an engine of your car')
            bot.register_next_step_handler(msg,  process_engine_step)

    except Exception as e:
        logger.error(e)
        bot.reply_to(message,  'Something went wrong')
        contacts.contacts_msg(message)
