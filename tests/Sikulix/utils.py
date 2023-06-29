from sikuli import *
import time

dir_browser = "C:\Users\miror\AppData\Local\Programs\Opera\opera.exe"

def open_browser():
    global temp
    temp = App.open(dir_browser)
    temp.focus()
    time.sleep(5)

def close_browser():
    global temp
    temp.close()

def send_message(msg):
    type("1683649654740.png", msg+Key.ENTER)
    Debug.info('Message '+msg+' was sent')
    time.sleep(2)

def click_if_exists(img):
    if exists(img):
        click(img)
        time.sleep(2)
        return True
    Debug.info("Image wasn't found")
    time.sleep(2)
    return False

def type_if_exists(img, msg):
    if exists(img):
        type(img, msg)
        time.sleep(2)
        return True
    Debug.info("Image wasn't found")
    time.sleep(2)
    return False
    
