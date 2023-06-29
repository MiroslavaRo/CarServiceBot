"""User contact information module"""
import sqlite3
import os
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import credentials
import design
import texts

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Bot instance
bot = credentials.bot
MAX_CARS = credentials.MAX_CARS


def user_info(user_id):
    """Retrive user info from database"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users WHERE chat_id = ?', (user_id, ))
    user_data = cur.fetchone()

    cur.execute('SELECT * FROM cars WHERE user = ?', (user_id, ))
    cars_data = cur.fetchall()

    cars = []
    if cars_data:
        for car in cars_data:
            car_info = {
            'car_id': car[0],
           'brand': car[1],
           'model':car[2],
           'year': car[3],
           'engine': car[4],
           'tech_passport': car[5]
            }
            cars.append(car_info)

    if user_data:
        user_info_var = {
            'chat_id': user_data[0],
           'username': user_data[1],
           'full_name': user_data[2],
           'phone': user_data[3],
           'email': user_data[4],
           'carlist': cars
        }
        logger.warning(user_info_var)

        con.close()
        return user_info_var
    return None


def contacts_butns():
    """Buttons for user info post (Change/Appotments)"""
    button_list = [
        InlineKeyboardButton("🚘Add car", callback_data = 'add_car'),
        InlineKeyboardButton("⚒Change information", callback_data = 'change'),
         InlineKeyboardButton("✍️Appointments", callback_data = 'appoitments')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 1))

    return reply_markup

def register_butn():
    """Register markup"""
    button_list = [
        InlineKeyboardButton("Register", callback_data = 'reg')
    ]
    reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols = 1))

    return reply_markup

def contacts(call):
    """User's contact information."""

    # Try to retrive user info from DB
    user = user_info(call.from_user.id)

    if user is None:
        text = "❌ You are not registered yet. \nSign in? ✅"
        bot.send_message(call.from_user.id, text, parse_mode = 'html', reply_markup = register_butn())

    else:
        fullname = user['full_name']
        if user['phone'] is not None:
            phone = user['phone']
        else:
            phone = '-'

        if user['email'] is not None:
            email = user['email']
        else:
            email = '-'

        cars = ''
        if user['carlist'] is not None:
            cars = '\n<b>🚘Your cars:</b>\n'

            for index, car in enumerate(user['carlist']):
                brand = car['brand']
                model = car['model']
                year = car['year']
                engine = car['engine']
                if(brand is None) | (model is None) | (year is None):
                    car_txt = "Your tech passport processing."
                else:
                    car_txt = f"{brand} {model} {year} {engine}"
                cars += f'''{(index+1)}. {car_txt}\n'''

        contact = f'<b>Your contact information:</b>\n\n👤{fullname}\n📞Tel.:{phone}\n📧 Email: {email}\n'

        text = contact + cars

        logger.warning("Call msg: ", call.message.text)
        if (call.message.text is None) | (call.message.text == texts.WELCOME_TEXT):
            bot.send_message(call.from_user.id, text,
           parse_mode = 'html', reply_markup = contacts_butns())
        else:
            bot.edit_message_text(text, call.from_user.id,
           call.message.message_id,
           parse_mode = 'html',
           reply_markup = contacts_butns())
            bot.send_message(call.from_user.id,
           texts.KEYBOARD,
           parse_mode = 'html',
           reply_markup = design.keyboard())


@bot.message_handler(commands = ["profile"])
def contacts_msg(message):
    """Copy for message not callback"""
    user = user_info(message.from_user.id)

    if user is None:
        text = "❌ You are not registered yet. \nSign in? ✅?"
        bot.send_message(message.from_user.id, text, parse_mode = 'html', reply_markup = register_butn())

    else:
        fullname = user['full_name']
        if user['phone'] is not None:
            phone = user['phone']
        else:
            phone = '-'

        if user['email'] is not None:
            email = user['email']
        else:
            email = '-'

        cars = ''
        if user['carlist'] is not None:
            cars = '\n<b>🚘Your cars:</b>\n'

            for index, car in enumerate(user['carlist']):
                brand = car['brand']
                model = car['model']
                year = car['year']
                engine = car['engine']
                if(brand is None) | (model is None) | (year is None):
                    car_txt = "Your tech passport processing."
                else:
                    car_txt = f"{brand} {model} {year} {engine}"
                cars += f'''{(index+1)}. {car_txt}\n'''

        contact = f'<b>Your contact information:</b>\n\n👤{fullname}\n📞Tel.:{phone}\n📧 Email: {email}\n'
        text = contact + cars
        bot.send_message(message.from_user.id, text, parse_mode = 'html', reply_markup = contacts_butns())


def save_data(call, user):
    """Save user function"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    try:
        cur.execute('''INSERT OR REPLACE INTO users (chat_id, username, full_name, phone, email)
        VALUES (?, ?, ?, ?, ?)''',
       (call.from_user.id, call.from_user.username, user.name, user.phone, user.email))

        con.commit()
        bot.answer_callback_query(call.id, "Data saved successfully!")
    except Exception as e:
        logger.error(f"{type(e)} error occurred: {e}")
        bot.answer_callback_query(call.id, "Failed to save")
    contacts(call)

def save_car(call, car):
    """Save car function"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    tech_passport = None
    cur.execute('SELECT * FROM cars WHERE car_id = ?', (car.car_id, ))
    cars_data = cur.fetchone()
    if cars_data:
        if cars_data[5] is not None:
            tech_passport = cars_data[5]
    car.tech_passport = tech_passport

    logger.warning(car.car_id, car.brand, car.model,
   car.year, car.engine, car.tech_passport, call.from_user.id)

    try:
        cur.execute('''INSERT OR REPLACE INTO cars (car_id, brand, model, year, tech_passport, engine, user)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
           (car.car_id, car.brand, car.model, car.year, car.tech_passport, car.engine, call.from_user.id))

        con.commit()
        bot.answer_callback_query(call.id, "Data saved successfully!")
    except Exception as e:
        logger.error(f"{type(e)} error occurred: {e}")
        bot.answer_callback_query(call.id, "Failed to save")
    contacts(call)

def car_delete(call, car_id):
    """Delete car function"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()

    cid = call.from_user.id

    logger.warning(f"chat_id:{cid}, car_id:{car_id}")

    try:
        cur.execute('SELECT * FROM cars WHERE user = ?', (cid, ))
        cars_data = cur.fetchall()
        delete_path = cars_data[car_id%10][5]
        if delete_path is not None and os.path.exists(delete_path):
            os.remove(delete_path)
        cars_data.pop(car_id%10)
        cars = []
        for car in cars_data:
            car_info = {
            'car_id': car[0],
           'brand': car[1],
           'model': car[2],
           'year': car[3],
           'engine': car[4],
           'tech_passport': car[5]
            }
            if car_info['car_id'] > car_id:
                car_info['car_id'] -= 1
            cars.append(car_info)

        cur.execute(f'DELETE FROM cars WHERE user = {cid}')
        for car in cars:
            path = car['tech_passport']
            new_path = None
            file = None
            if path is not None and path != '':
                with open(path, "rb") as code:
                    file = code.read()
                if file is None:
                    break
                os.remove(path)
                new_path = f"./imgs/cars/{call.from_user.id}/{car['car_id']}.png"
                with open(new_path, "wb") as code:
                    code.write(file)

            cur.execute('''INSERT OR REPLACE INTO cars
                (car_id, brand, model, year, tech_passport, engine, user)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (car['car_id'],
             car['brand'],
             car['model'],
             car['year'],
             new_path,
             car['engine'],
             call.from_user.id))

        con.commit()
        bot.answer_callback_query(call.id, "Car removed successfully!")
    except Exception as e:
        logger.error(f"{type(e)} error occurred: {e}")
        bot.answer_callback_query(call.id, "Failed to remove")
    contacts(call)

def save_techpass(call, car):
    """Save tachpassport"""
    con = sqlite3.connect("supercar.db")
    cur = con.cursor()
    try:
        path = f"./imgs/cars/{call.from_user.id}"
        if not os.path.exists(path):
            os.mkdir(path)
            logger.warning(f"Folder {path} created!")
        else:
            logger.warning(f"Folder {path} already exists")

        path += f"/{car.car_id}.png"
        logger.warning(path)

        with open(path, "wb") as code:
            code.write(car.tech_passport)

        cur.execute(f'''SELECT * FROM cars WHERE car_id = {car.car_id}''')
        car_data = cur.fetchall()

        if len(car_data) != 0:
            cur.execute(f'''UPDATE cars SET tech_passport = "{path}" WHERE car_id = {car.car_id}''')
        else:
            cur.execute('''INSERT OR REPLACE INTO cars
                (car_id, brand, model, year, engine, tech_passport, user)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (car.car_id, None, None, None, None, path, call.from_user.id))

        con.commit()
        bot.answer_callback_query(call.id, "Tech passport saved successfully!")
    except Exception as e:
        logger.error(f"{type(e)} error occurred: {e}")
        bot.answer_callback_query(call.id, "Failed to save tech passport")
    contacts(call)
