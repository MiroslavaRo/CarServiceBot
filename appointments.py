"""Appointments module"""
import logging
import datetime
from datetime import datetime
import sqlite3
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import models
import services
import design
import credentials
import caregistration
import contacts

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Bot instance
bot = credentials.bot

apps_dict = models.apps_dict
apps = []

def app_info(user_id):
    """Retrive appointments info from databaset"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    user = contacts.user_info(user_id)

    cur.execute('SELECT * FROM appointments WHERE user = ?',(user_id, ))
    app_data = cur.fetchall()
    apps.clear()

    if app_data:
        for app in app_data:
            apointment_info = {
            'app_id': app[0],
            'app_date': app[1],
            'comments':app[2],
            'photo': app[3],
            'service_id': app[4],
            'user': app[5],
            'car': app[6]
            }
            apps.append(apointment_info)

        user['appointments'] = apps
        return user
    return None

def display_apps(call):
    """Displays user's appointment"""
    cid = call.from_user.id
    user = app_info(call.from_user.id)

    if user is not None:
        if user['appointments']:
            text = '\n<b>📝Your appointments📝</b>\n'
            bot.send_message(cid, text, parse_mode = 'html')

            logger.warning(len(user['appointments']))

            for index, app in enumerate(user['appointments']):
                app_date = app['app_date']
                comments = app['comments']
                service = services.service_info(app['service_id'])
                car_id = app['car']
                car = []
                for uscar in user['carlist']:
                    if uscar['car_id'] == car_id:
                        car = uscar
                        break
                    carmsg = 'Your tech passport processing...'
                if car['brand'] is not None:
                    carmsg = f"{car['brand']} {car['model']} {car['year']}({car['engine']})"

                app_txt = f"""🔺<b>Appointment №{index+1}</b>

✅ <b>Date</b>: {app_date}

✅ <b>Service</b>: {service['service_name']}(<b>from BGN {service['price']}</b>)

✅ <b>Details</b>: {comments}

✅ <b>Car</b>: {carmsg}

✅ <b>Contact information</b>: {user['full_name']} {user['phone']}"""
                text = app_txt+"\n"
                bot.send_message(cid, app_txt, parse_mode = 'html')#, reply_markup = action_app())
    else:
        text = "❌ You have no appointments."
        bot.send_message(cid, text, parse_mode = 'html')

def action_app():
    """Buttons for changing/deleting appointment"""
    button_list = [
        InlineKeyboardButton("Change", callback_data = "change_app"),
        InlineKeyboardButton("Delete", callback_data = "delete_app")
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 2))
    return reply_markup

# REGISTRATION----------------------------------------
def service_action(call, service_name):
    """Proceed with appointment creation with chosen service"""
    cid = call.from_user.id
    name = service_name
    service = services.services_info(name)
    logger.warning(service)
    try:
        app = models.Apointment(cid)
        apps_dict[cid] = app
        app = apps_dict[cid]
        app.service = service['service_id']
        app.service_name = service_name

        con = sqlite3.connect("supercar.db")
        cur = con.cursor()
        cur.execute('SELECT * FROM appointments ORDER BY app_id DESC LIMIT 1;')
        app_data = cur.fetchone()
        logger.warning("app_data: ", app_data)

        if app_data:
            if app_data is not None:
                app.app_id = app_data[0]+1
            else:
                app.app_id = 1
        else:
            app.app_id = 1

        logger.warning('Index: ', app.app_id)

        text = "✍️ Describe the desired work in details."

        if(service_name == "maintenance") | (service_name == "comprehensive maintenance"):
            text = services.maintence_components()
            msg = bot.send_message(cid, text, parse_mode = 'html', reply_markup = design.keyboard())
            bot.register_next_step_handler(msg, process_comments_step)

        elif(service_name == "painting") | (service_name == "polishing") | (service_name == "scaffolding"):
            text = '''📝 Enter the details
Describe the extent of the damage(For example: a scratched bumper). 🚘
'''
            msg = bot.send_message(cid, text, parse_mode = 'html', reply_markup = design.keyboard())
            bot.register_next_step_handler(msg, process_comments_step)
        else:
            msg = bot.send_message(cid, text, parse_mode = 'html', reply_markup = design.keyboard())
            bot.register_next_step_handler(msg, process_comments_step)

    except Exception as e:
        bot.send_message(cid, 'Unfortunetly, service unavailable 😔')

def process_comments_step(message):
    """Processing comments for service"""
    logger.warning(f"Text msg: {message.text}")
    cid = message.from_user.id

    app = apps_dict[cid]
    app.comments = message.text

    servs = ["painting", 'scaffolding', 'polishing', 'repair']

    if app.comments.lower() in design.all_keywords:
        design.handle_menu_click(message)

    elif app.service_name in servs:
        text = "You can add a photo of the damage.📸"
        button_list = [
            InlineKeyboardButton("Add photo", callback_data = 'addmorephoto'),
            InlineKeyboardButton("Skip", callback_data = 'continue_calendar')
        ]
        reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 1))
        bot.send_message(cid, text, reply_markup = reply_markup)

    else:
        text = "📆Choose a date from the calendar."
        photo = open('imgs/calendar.jpg', 'rb')
        button_list = [
        InlineKeyboardButton("Open Calendar", url = 'https://google.com'),
        InlineKeyboardButton("Done", callback_data = 'continue_contacts' )
        ]
        reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 1))
        bot.send_photo(cid, photo, text, reply_markup = reply_markup)

def convertToBinaryData(filename):
    """Converting file in binary format"""
    with open(filename, 'rb') as file:
        blob_вata = file.read()
    return blob_вata

def process_damage_step(message):
    """Save photo of damage"""
    logger.warning(message.text)

    cid = message.chat.id
    app = apps_dict[cid]

    try:
        if(message.text is not None) & (message.text in design.all_keywords):
            design.handle_menu_click(message)
        elif message.text is not None:
            msg = bot.reply_to(message, 'Please send photo')
            bot.register_next_step_handler(msg, process_damage_step)
        else:
            file_path = bot.get_file(message.photo[0].file_id).file_path
            file = bot.download_file(file_path)

            path = f"./imgs/appointments/{app.app_id}/"
            if not os.path.exists(path):
                os.mkdir(path)
                logger.warning(f"Folder {path} created!")
            else:
                logger.warning(f"Folder {path} already exists")
            with open(path+f"/{message.photo[0].file_id}.png", "wb") as code:
                code.write(file)

            app.photo = path+f"/{message.photo[0].file_id}.png"

            logger.warning('App photo: ', app.photo)

            button_list = [
                #InlineKeyboardButton("Add more", callback_data = 'addmorephoto'),
                InlineKeyboardButton("To next step", callback_data = 'continue_calendar')
            ]
            reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 1))
            text = "Continue?"
            bot.reply_to(message, text, reply_markup = reply_markup)

    except Exception as e:
        logger.error("%s error occurred: %s", type(e), e)


def calendar_step_handler(message):
    """Book appointment date"""
    cid = message.chat.id
    app = apps_dict[cid]
    date = datetime.now()
    app.app_date = date.date()

    user = contacts.user_info(cid)

    if user is None:
        text = "❌ You are not registered yet. \nSign in? ✅"
        bot.send_message(cid, text, parse_mode = 'html', reply_markup = contacts.register_butn())

    else:
        fullname = user['full_name']
        if user['phone'] is not None:
            phone = user['phone']
        else: phone = '-'

        if user['email'] is not None:
            email = user['email']
        else: email = '-'

        contact = f'<b>Your contact information:</b>\n\n👤{fullname}\n📞Tel.:{phone}\n📧Email:{email}'
        bot.send_message(cid, contact, parse_mode = 'html', reply_markup = change_contact())

def change_contact():
    """Change contact"""
    button_list = [
        InlineKeyboardButton("Continue", callback_data = 'continue_app'),
        InlineKeyboardButton("Change information", callback_data = 'change')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 2))
    return reply_markup

def choose_car(call):
    """Ask for car_id in keyboard(caregistration.py)"""
    cid = call.from_user.id
    caregistration.change_car  = 'choose'
    bot.send_message(cid, 'Choose car to sign up',
                     reply_markup = caregistration.change_car_buttons(cid))

def car_for_app(message, car_id):
    """Chosing car for appointment"""
    cid = message.from_user.id
    app = apps_dict[cid]
    app.car = car_id

    user = contacts.user_info(cid)
    service = services.service_info(app.service)

    car = None
    carmsg = f'{car_id}'
    for uscar in user['carlist']:
        if uscar['car_id'] == car_id:
            car = uscar
    carmsg = 'Your tech passport processing...'
    if car['brand'] is not None:
        carmsg = f"{car['brand']} {car['model']} {car['year']}({car['engine']})"
    logger.warning(carmsg)

    info = f"""🔺<b>Appointment</b>

✅ <b>Date</b>: {app.app_date}

✅ <b>Service</b>: {service['service_name']}(<b>from BGN {service['price']}</b>)

✅ <b>Details</b>: {app.comments}

✅ <b>Car</b>: {carmsg}

✅ <b>Contact info</b>: {user['full_name']} {user['phone']}"""
    text = info+ "\n\n<b>Save changes?</b>"
    bot.send_message(cid, text, parse_mode = 'html', reply_markup = reg_app_buttons())

def cancel_app(call):
    """Cancel appointment"""
    cid = call.from_user.id
    mid = call.message.message_id
    bot.edit_message_text(call.message.text, cid, mid)
    caregistration.change_car  = 'change'
    services.price_call(call)

def reg_app_buttons():
    """Function printing python version."""
    button_list = [
        InlineKeyboardButton("Yes", callback_data = 'save_app'),
        InlineKeyboardButton("No", callback_data = 'cancel_app')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 2))
    return reply_markup

def save_app(call, app):
    """Saving appointment"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    logger.warning(app.app_id,
                   app.app_date,
                   app.comments,
                   app.photo,
                   app.service,
                   call.from_user.id,
                   app.car)

    try:
        cur.execute('''INSERT OR REPLACE INTO appointments
       (app_id, app_date, comments, photo, service, user, car)
                VALUES(?, ?, ?, ?, ?, ?, ?)''',
           (app.app_id, app.app_date, app.comments, 
            app.photo, app.service, call.from_user.id, app.car))

        con.commit()
        bot.answer_callback_query(call.id, "Data saved successfully!")
        services.price_call(call)

    except Exception as e:
        logger.error("%s error occurred: %s", type(e), e)
        bot.answer_callback_query(call.id, "Failed to save")

    contacts.contacts(call)

def delete_app(call, app):
    """Deleting appointment"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    logger.warning(app.app_id,
                   app.app_date,
                   app.comments,
                   app.photo,
                   app.service,
                   call.from_user.id,
                   app.car)

    try:
        cur.execute(f'''DELETE FROM appointments WHERE user = {app.app_id}''')
        con.commit()
        bot.answer_callback_query(call.id, "Appointment canceled!")
        services.price_call(call)

    except Exception as e:
        logger.error("%s error occurred: %s", type(e), e)
        bot.answer_callback_query(call.id, "Failed to cancel")
