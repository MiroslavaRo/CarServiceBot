"""Main program starts bot"""
import logging
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup,  InlineKeyboardButton
import credentials
import design
import contacts
import models
import texts
import registration
import services
import appointments
import caregistration



logger = logging.getLogger()


# Bot instance
bot = credentials.bot

con = sqlite3.connect("supercar.db")
c = con.cursor()

user_dict = models.user_dict
apps_dict = models.apps_dict
apps = appointments.apps
car_dict = models.car_dict
MAX_CARS = credentials.MAX_CARS

# -------------------COMMANDS MENU------------------------
bot.set_my_commands([
    telebot.types.BotCommand("/start",  "Welcome message"),
    telebot.types.BotCommand("/help",  "Information about bot"),
    telebot.types.BotCommand("/aboutus",  "Information about our company"),
    telebot.types.BotCommand("/services",  "Information about available services and products"),
    telebot.types.BotCommand("/profile",  "Your profile information"),
    telebot.types.BotCommand("/question",  "Ask a question or share your suggestion")
])


# ------------------0. WELCOME---------------------------

# Button response
@bot.callback_query_handler(func=lambda message: True)
def button_press_handler(call):
    """Call back queries"""

    data = call.data

    if data == 'contacts':
        design.company_info(call)

    elif data == 'sap':
        bot.send_message(call.from_user.id, "Services options 👇",  reply_markup = services.keyboard_services())

    elif data == 'profile':
        contacts.contacts(call)

    elif data == 'reg':
        registration.registration(call)

    elif data == 'change':
        registration.part_registration(call)

    elif data == 'appoitments':
        appointments.display_apps(call)

    elif data == 'save_user':
        user = user_dict[call.from_user.id]
        logger.warning(f'{user.name}\tTel.:{user.phone}\tEmail:{user.email}')
        contacts.save_data(call,  user_dict[call.from_user.id])

    elif data == 'cancel_user':
        contacts.contacts(call)

    # CAR SAVE/CANCEL
    elif data == 'add_car':
        car = models.Car(call.from_user.id)
        if contacts.user_info(call.from_user.id)['carlist'] is None:
            car_index = 0
        else:
            car_index = len(contacts.user_info(call.from_user.id)['carlist'])
        car.car_id = call.from_user.id*MAX_CARS+car_index
        car_dict[call.from_user.id] = car
        logger.warning(f"car_id:{car_dict[call.from_user.id].car_id},  car_index:{car_index}")
        caregistration.car_registration(call.message)

    elif data == 'change_car':
        caregistration.car_change(call)

    elif data == 'manually':
        caregistration.manual_reg_step(call)

    elif data == 'tech_pass':
        caregistration.tech_pass_step(call)

    elif data == 'save_car':
        car = car_dict[call.from_user.id]
        logger.warning(f'Brand:{car.brand}\tModel:{car.model}\tYear:{car.year}\tEngine:{car.engine}')
        contacts.save_car(call,  car_dict[call.from_user.id])

    elif data == 'cancel_car':
        contacts.contacts(call)

    elif data == 'delete_car':
        contacts.car_delete(call, car_dict[call.from_user.id].car_id)

    elif data == 'cancel_delete':
        contacts.contacts(call)

    elif data == 'save_techpass':
        design.remove_last_bot_message_buttons()
        contacts.save_techpass(call, car_dict[call.from_user.id])

    elif data == 'cancel_techpass':
        design.remove_last_bot_message_buttons()
        contacts.contacts_msg(call)

    # SERVICES

    elif data == "under_diagnostic":
        services.under_diagnostic(call.from_user.id)

    elif data == "comp_diagnostic":
        services.comp_diagnostic(call.from_user.id)

    # APPOINTMENTS

    elif data == "maintenance":
        appointments.service_action(call, 'maintenance')

    elif data == "comprehensive_maintenance":
        appointments.service_action(call, 'comprehensive maintenance')

    elif data == 'undercarriage':
        appointments.service_action(call, "undercarriage diagnostics")

    elif data == 'repair':
        appointments.service_action(call, "repair")

    elif data == 'computer':
        appointments.service_action(call, "computer diagnostics")

    elif data == 'painting':
        appointments.service_action(call, "painting")

    elif data == 'scaffolding':
        appointments.service_action(call, "scaffolding")

    elif data == 'polishing':
        appointments.service_action(call, "polishing")

    elif data == 'scaffolding_painting':
        appointments.service_action(call, "scaffolding_painting")

    elif data == 'p_everything':
        appointments.service_action(call, "p_everything")

    elif data == 'conditioner':
        appointments.service_action(call, "refueling air conditioner")

    elif data == "continue_app":
        appointments.choose_car(call)
    elif data == "addmorephoto":
        appointments.process_damage_step(call.message)

    elif data == 'continue_calendar':
        text = "📆Choose a date from the calendar."
        photo = open('imgs/calendar.jpg',  'rb')
        button_list = [
        InlineKeyboardButton("Open Calendar",  url='https://google.com'),
        InlineKeyboardButton("Done",  callback_data='continue_contacts')
        ]
        reply_markup = InlineKeyboardMarkup(design.build_menu(button_list,  n_cols=1))
        bot.send_photo(call.from_user.id, photo,  text, reply_markup = reply_markup)
        #bot.register_next_step_handler(msg,  appointments.calendar_step_handler)

    elif data == "continue_contacts":
        appointments.calendar_step_handler(call.message)

    elif data == 'save_app':
        app = apps_dict[call.from_user.id]
        appointments.save_app(call,  app)

    elif data == 'cancel_app':
        appointments.cancel_app(call)

    elif data[:10] == 'change_app': # transfer app_id in callback data(do slice)
        # app_id = int(data[10:])
        pass

    elif data[:10] == 'delete_app': # transfer app_id in callback data(do slice)
        # app_id = int(data[10:])
        pass

start_commands = ["start",  "home"]
@bot.message_handler(start_commands)
def send_welcome(message):
    """Welcome message"""
    photo = open('imgs/welcome.jpg',  'rb')
    bot.send_photo(message.from_user.id,  photo,  texts.WELCOME_TEXT,  parse_mode='html', reply_markup = design.welcome_message_with_buttons())
    bot.send_message(message.from_user.id, texts.KEYBOARD, parse_mode='html',  reply_markup = design.keyboard())

start_commands = ["help"]
@bot.message_handler(start_commands)
def send_help(message):
    """HELP message"""
    bot.send_message(message.from_user.id,  texts.HELP_TEXT, parse_mode='html', reply_markup = design.welcome_message_with_buttons())
    bot.send_message(message.from_user.id, texts.KEYBOARD, parse_mode='html',  reply_markup = design.keyboard())

@bot.message_handler(func=lambda message: message.text.lower() in design.menu_ask_options)
@bot.message_handler(commands=["question"])
def send_ask(message):
    """Question message"""
    button_list = [
        InlineKeyboardButton("Chat with manager",  url='https://t.me/')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list,  n_cols=1))
    bot.send_message(message.from_user.id, texts.ASK, parse_mode='html', reply_markup = reply_markup)

@bot.message_handler(func=lambda message: message.text.lower() in design.menu_price_services)
@bot.message_handler(commands=["services"])
def send_price(message):
    """Price message"""
    services.price_msg(message)
    bot.send_message(message.from_user.id, "Services options 👇",  reply_markup = services.keyboard_services())


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

# Start the bot
bot.polling()
