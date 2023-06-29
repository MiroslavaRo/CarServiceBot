
import sqlite3

# Create a connection to the database
con = sqlite3.connect("supercar.db")
c = con.cursor()

# USERS
c.execute('''CREATE TABLE IF NOT EXISTS users
             (chat_id INTEGER PRIMARY KEY,
              username TEXT,
              full_name TEXT,
              phone TEXT,
              email TEXT)''')


# CARS
c.execute('''CREATE TABLE IF NOT EXISTS cars
             (car_id INTEGER PRIMARY KEY,
              brand TEXT,
              model TEXT,
              year INTEGER,
              engine TEXT,
              tech_passport BLOB,              
              user INTEGER,              
              FOREIGN KEY(user) REFERENCES users(chat_id))''')

# SERVICES
c.execute('''CREATE TABLE IF NOT EXISTS services
             (service_id INTEGER PRIMARY KEY,
              service_name TEXT,
              service_info TEXT,
              price REAL
              )''')

c.execute('''INSERT INTO services (service_name, service_info, price)
VALUES ('undercarriage diagnostics','',20),
('computer diagnostics','',25),
('maintenance','',40),
('comprehensive maintenance','',80),
('refueling air conditioner','',30),
('painting','1 element',150),
('scaffolding','',70),
('polishing','',30);''')

# APPOINTMENT
c.execute('''CREATE TABLE IF NOT EXISTS appointments
             (app_id INTEGER PRIMARY KEY,
              app_date TEXT,
              comments TEXT,
              photo BLOB,
              service INTEGER,
              user INTEGER,
              car INTEGER,
              FOREIGN KEY(service) REFERENCES services(service_id),
              FOREIGN KEY(user) REFERENCES users(chat_id),
              FOREIGN KEY(car) REFERENCES cars(car_id)
              )''')


con.commit()

