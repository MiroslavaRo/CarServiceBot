"""Services"""
import sqlite3
import logging
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import credentials
import design
import models
import texts

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Bot instance
bot = credentials.bot

services_dict = models.services_dict

def service_info(service_id):
    """Gets data about services by its id from data base"""
    con = sqlite3.connect("supercar.db")
    cursor = con.cursor()

    cursor.execute('SELECT * FROM services WHERE service_id=?', (service_id, ))
    service_var = cursor.fetchone()

    if service_var:
        service_info_var = {
            'service_id': service_var[0],
            'service_name': service_var[1],
            'service_info': service_var[2],
            'price': service_var[3]
        }

        con.close()
        return service_info_var
    return None


def services_info(service_name):
    """Gets data about services by its name from data base"""
    con = sqlite3.connect("supercar.db")
    cursor = con.cursor()

    cursor.execute('SELECT * FROM services WHERE service_name=?', (service_name, ))
    service_var = cursor.fetchone()

    if service_var:
        service_info_var = {
            'service_id': service_var[0],
            'service_name': service_var[1],
            'service_info': service_var[2],
            'price': service_var[3]
        }

        con.close()
        return service_info_var
    return None

def service(name):
    """Gets info about specific service and saves it into global variable services_dict"""
    service_var = services_info(name)
    if service_var is not None:
        srvc = models.Service(name)
        srvc.name = service_var['service_name']
        srvc.price = service_var['price']

        services_dict[name] = srvc
        return srvc
    return None

# ------------------------------PRICELIST------------------------------
def pricelist():
    """Constructs info about pricelist into message and returns"""
    name = 'undercarriage diagnostics'
    undercarriage_msg = ''
    if service(name) is not None:
        undercarriage_msg = f'''
   -  Undercarriage diagnostics - <b>BGN {services_dict[name].price}</b>;'''

    name = 'computer diagnostics'
    comp_diagnostic_msg = ''
    if service('computer diagnostics') is not None:
        comp_diagnostic_msg = f'''
   -  Computer diagnostics - <b>BGN {services_dict[name].price}</b>;'''

    name = 'maintenance'
    maintenance_msg = ''
    if service('maintenance') is not None:
        maintenance_msg = f'''
   -  Maintenance - <b>from BGN {services_dict[name].price}</b>;'''

    name = 'painting'
    painting_msg = ''
    if service(name) is not None:
        painting_msg = f'''
   -  Painting, scaffolding of a car - <b>from BGN {services_dict[name].price}</b>;'''

    # scaffolding = service('scaffolding')

    name = 'polishing'
    polishing_msg = ''
    if service(name) is not None:
        polishing_msg = f'''
   -  Car polishing - <b>from BGN {services_dict[name].price}</b>.'''

    for i in services_dict:
        design.service_names.append(services_dict[i].name)

    text = f'''🎩 Our company provides a wide range of services.
You can learn about each in detail by selecting an option in the keyboard!
    
    💸 <b>Price list</b> 💸
{undercarriage_msg}{comp_diagnostic_msg}{maintenance_msg}{painting_msg}{polishing_msg}

❗️ <b>Please note that prices may vary depending on the complexity of the work. ✅</b>
'''
    return text

def price_call(call):
    """Sends pricelist to user as message (accepts call as a parameter)"""
    text = pricelist()
    bot.send_message(call.from_user.id, text, parse_mode='html', reply_markup=keyboard_services())

def price_msg(message):
    """Sends pricelist to user as message (accepts message as a parameter)"""
    text = pricelist()
    bot.send_message(message.from_user.id, text, parse_mode='html', reply_markup=keyboard_services())

# ------------------2.SERVICES---------------------

services_btns = [
    "🔍Diagnostics", "💧Maintenance", "💨Conditioner", "🌈Painting", "🪛Repair",
    "⬅️Back", "Ask question❓"
]

def keyboard_services():
    """Returns buttons to choose specific service"""
    menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍Diagnostics")
    btn2 = types.KeyboardButton("💧Maintenance")
    btn3 = types.KeyboardButton("💨Conditioner")
    btn5 = types.KeyboardButton("🌈Painting")
    btn6 = types.KeyboardButton("🪛Repair")
    btn_back = types.KeyboardButton("⬅️Back")
    btn_ask = types.KeyboardButton("Ask question❓")

    menu_keyboard.add(btn1, btn2, btn3, btn5, btn6).add(btn_back, btn_ask)
    return menu_keyboard


@bot.message_handler(func=lambda message: message.text in services_btns)
@bot.message_handler(func=lambda message: message.text.lower() in design.service_names)
def handle_menu_click(message):
    """Displays menu-message that displays and allows to choose specific service"""
    cid = message.from_user.id
    if (message.text == "🔍Diagnostics") | (message.text.lower() in design.key_diagnostics):
        photo = open('imgs/diagnostics.jpg', 'rb')
        bot.send_photo(cid, photo, texts.DIAGNOSTICS, parse_mode='html', reply_markup = diagn_bttns())
    elif (message.text == "💧Maintenance") | (message.text.lower() in design.key_maintenance):
        maintence(message)
    elif (message.text == "💨Conditioner") | (message.text.lower() in design.key_conditioner):
        conditioner(message)
    elif (message.text == "🌈Painting") | (message.text.lower() in design.key_paint):
        painting(message)
    elif (message.text == "🪛Repair") | (message.text.lower() in design.key_repair):
        photo = open('imgs/repair.jpg', 'rb')
        photo = open('imgs/repair.jpg', 'rb')
        bot.send_photo(cid, photo, "Sign up for repair", parse_mode='html', reply_markup = signup('repair')) # comments
    elif message.text == "⬅️Back":
        # bot.send_message(cid, "How can we help you?", reply_markup = design.keyboard())
        photo = open('imgs/welcome.jpg', 'rb')
        bot.send_photo(cid, photo, texts.WELCOME_TEXT, parse_mode='html', reply_markup = design.welcome_message_with_buttons())
        bot.send_message(cid, texts.KEYBOARD, parse_mode='html', reply_markup = design.keyboard())
    elif message.text == "Ask question❓":
        button_list = [
        InlineKeyboardButton("Chat with manager", url='https://t.me/ryuVitoshi')
        ]
        reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=1))
        photo = open('imgs/question.jpg', 'rb')
        bot.send_photo(cid, photo, texts.ASK, parse_mode='html', reply_markup = reply_markup)


def signup(service_name):
    """Allows user to sign up to specific service"""
    button_list = [
        InlineKeyboardButton("Sign up", callback_data=service_name)
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=2))
    return reply_markup
# ---------------------SERVICES INFO--------------

# DIAGNOSTIC------------------------------
def diagn_bttns():
    """Returns buttons to chose diagnostics"""
    button_list = [
        InlineKeyboardButton("Undercarriage diagnostics", callback_data = "under_diagnostic"),
         InlineKeyboardButton("Computer diagnostics", callback_data = "comp_diagnostic")
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=2))
    return reply_markup

def under_diagnostic(chat_id):
    """Displays info about diagnostics"""
    name = 'undercarriage diagnostics'
    if service(name) is not None:
        photo = open('imgs/under.jpg', 'rb')
        bot.send_photo(chat_id, photo, f'''⚙️<b>Undercarriage diagnostics</b>⚙️

✅ We will carry out a qualitative inspection of <b>all components and elements</b> of the chassis that affect safety and quality of driving.
✅ We will also advise on the replacement of auto parts.

💸 Estimated price – <b>BGN {services_dict[name].price}</b>.

👍If necessary, we can also <b>order new spare parts or carry out repairs</b>, after agreement with you.
💸 The price of this service depends on the complexity of the work, approximately from <b>BGN {services_dict[name].price+15}</b>.

<b>Sign up</b> for undercarriage diagnosis 👇👇👇''', 
parse_mode='html', reply_markup = signup('undercarriage'))

    else:
        text = "Unfortunetly, service unavailable 😔"
        bot.send_message(chat_id, text, parse_mode='html')


def comp_diagnostic(chat_id):
    """Displays info about computer diagnostics"""
    name = 'computer diagnostics'
    comp_diagnostic_var = service(name)
    if comp_diagnostic_var is not None:
        comp_diagnostic_price = services_dict[name].price
        photo = open('imgs/comp.jpg', 'rb')
        bot.send_photo(chat_id, photo, f'''🖥️<b>Computer diagnostics</b>🖥️

✅ We will check all <b>nodes and control units</b> of your car for the presence of errors that affect the safety and quality of driving.
❗️(The work is performed using <b>the official computer diagnostic software</b> LAUNCH X-431 PRO v4.0)

💸 Approximate price – <b>BGN {comp_diagnostic_price}</b>.

<b>Sign up</b> for computer diagnostics 👇👇👇''', parse_mode='html', reply_markup = signup('computer'))


# CAR MAINTENCES-------------------------------------
def maintence(msg):
    """Displays info about maintence"""
    maintenance = 'maintenance'
    comprehensive = 'comprehensive maintenance'
    if (service(maintenance) is not None) | (service(comprehensive) is not None):
        maintenance_price = services_dict[maintenance].price
        comprehensive_maintenance_price = services_dict[comprehensive].price

        text = f'''🔩<b>Car maintenance</b>🔩

This section includes the following services:
    1. Changing oil and filtering - <b>from BGN {maintenance_price}</b>.💧
    2. Comprehensive maintenance - <b>from BGN {comprehensive_maintenance_price}</b>.🩸
    (replacement of oil and filters, check of running gear and computer adjustment)

<b>Sign up</b> for maintenance 👇👇👇'''
        photo = open('imgs/maintenance.jpeg', 'rb')
        bot.send_photo(msg.from_user.id, photo, text, parse_mode='html', reply_markup=maintence_types())
    else:
        text = "Unfortunetly, service unavailable 😔"
        bot.send_message(msg.from_user.id, text, parse_mode='html')

def maintence_types():
    """Returns buttons for choosing maintence"""
    button_list = [
        InlineKeyboardButton("Maintenance", callback_data='maintenance'),
        InlineKeyboardButton("Comprehensive maintenance", callback_data='comprehensive_maintenance')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=1))
    return reply_markup

def maintence_components():  # maintence_components remove parameter call
    """Displays info about maintence_components"""
    text = '''📃 <b>Availability and ordering of components</b> 📃

✅ Indicate if you have oil and filters available (For example: 2 liters of oil, 4 filters).

✍️ Indicate if you need something to order:
    -	Oil 💧
    -	Filter 🛢️
    -	Everything 🗒️'''

    return text

# CONDITIONER------------------------------
def conditioner(msg):
    """Displays info about conditioner"""
    name = 'refueling air conditioner'
    cid = msg.from_user.id
    if service(name) is not None:
        conditioner_price = services_dict[name].price
        text = f'''🌀Refueling the air conditioner🌀

💸 The price depends on the volume of freon and additional work on system diagnostics.

Approximetly <b>BGN {conditioner_price}</b>.

    Sign up for a refueling the air conditioner 👇👇👇'''
        photo = open('imgs/conditioner.jpg', 'rb')
        bot.send_photo(cid, photo, text, parse_mode='html', reply_markup=signup('conditioner'))
    else:
        text = "Unfortunetly, service unavailable 😔"
        bot.send_message(cid, text, parse_mode='html')

# PAINTING------------------------------------
def painting(message):
    """Menu-message for choosing service"""
    paint_m = ''
    scaf_ = ''
    pol_m = ''
    paint = 'painting'
    if service(paint) is not None:
        painting_price = services_dict[paint].price
        paint_m = f"\n    -	Painting of 1 element - from <b>BGN {services_dict[paint].price}</b>;"

    scaf = 'scaffolding'
    if service(scaf) is not None:
        # scaffolding_paint_price = services_dict[scaf].price+painting_price
        scaf_ = f'''
    -	Scaffolding with painting – <b>from BGN {services_dict[scaf].price+painting_price}</b>;'''

    polishing = 'polishing'
    if service(polishing) is not None:
        polishing_price = services_dict[polishing].price
        pol_m = f"\n   -	Polishing - <b>from BGN {polishing_price}</b>."

    if (paint_m != '') & (scaf_!= '') & (pol_m != ''):
        text = f'''✨Scaffolding, painting, polishing of the car🎨

💸 The price depends on the volume of work and its urgency:
    {paint_m}{scaf_}{pol_m}

<b>Choose</b> the required variant and <b>sign up</b>👇👇👇'''
        photo = open('imgs/painting.jpg', 'rb')
        bot.send_photo(message.from_user.id, photo, text, parse_mode='html', reply_markup=pps_type())

    else:
        text = "Unfortunetly, service unavailable 😔"
        bot.send_message(message.from_user.id, text, parse_mode='html')


def pps_type():
    """Returns buttons for choosing required variant"""
    button_list = [
        InlineKeyboardButton("Painting", callback_data='painting'),
        InlineKeyboardButton("Scaffolding", callback_data='scaffolding'),
        InlineKeyboardButton("Polishing", callback_data='polishing'),
        InlineKeyboardButton("Scaffolding and painting", callback_data='scaffolding_painting'),
        InlineKeyboardButton("Everything", callback_data='p_everything')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=2))
    return reply_markup
