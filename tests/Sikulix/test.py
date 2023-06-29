from sikuli import *
import os
import sys
import time
import shutil

import utils
reload(utils)

path = "C:/Users/miror/OneDrive/Документи/Fernando codes/CarServiceChatbot/CarServiceChatbot/tests/Sikuli/ui_test_report.html"

import unittest
import HTMLTestRunner
reload(HTMLTestRunner)

Debug.on(0)

class ui_test_bot(unittest.TestCase):

    def setUp(self):
        Debug.info('Setup Called')
        if exists("1683660486977.png"):
            return
        utils.open_browser()
        click("1683648891338.png")
        time.sleep(2)
        type("1683649213223.png", 'Super Car Service')
        time.sleep(2)
        click("1683649834206.png")
        time.sleep(2)
        utils.click_if_exists("1683649942988.png")

    def tearDown(self):
        time.sleep(2)
        #utils.close_browser()
        Debug.info('Work Ended')

    def test_registration(self):
        utils.send_message('Home')
        utils.click_if_exists("1683656361323.png")
        if exists("1683656461097.png"):
            utils.click_if_exists("1683656495011.png")
            utils.send_message('Hanna Snow123')
            utils.send_message('@Hanna Snowwwwwwwwwwwwwwwwww')
            utils.send_message('Hanna Snow')
            utils.send_message('Wrong number')
            utils.send_message('-12345678901234')
            utils.send_message('+1234567890')
            utils.send_message('test.email.com')
            utils.send_message('test@email.com')
            #utils.click_if_exists("1683658513464.png")
            utils.click_if_exists("1683658449305.png")
        Debug.info('test 01 ended')

    def test_change_personal_info(self):
        utils.send_message('Home')
        utils.click_if_exists("1683656361323.png")
        utils.click_if_exists("1683659062611.png")
        utils.click_if_exists("1683659083125.png")
        utils.send_message('Ervin Andreas')
        utils.send_message('+9876543210')
        utils.send_message('-')
        utils.click_if_exists("1683658449305.png")
        Debug.info('test 02 ended')

    def test_add_car_mannualy(self):
        utils.send_message('Home')
        utils.click_if_exists("1683656361323.png")
        utils.click_if_exists("1683659263899.png")
        utils.click_if_exists("1683659276896.png")
        utils.send_message('Audi')
        utils.send_message('Skysphere')
        utils.send_message('wrongyear')
        utils.send_message('2024')
        utils.send_message('1959')
        utils.send_message('2003')
        utils.send_message('MX-8')
        utils.click_if_exists("1683658449305.png")
        Debug.info('test 03 ended')

    def test_change_car_techpass(self):
        utils.send_message('Home')
        utils.click_if_exists("1683656361323.png")
        utils.click_if_exists("1683659062611.png")
        utils.click_if_exists("1683659787664.png")
        utils.click_if_exists("1683659859006.png")
        utils.click_if_exists("1683659878853.png")
        utils.click_if_exists("1683659913568.png")
        utils.send_message('wrongphoto')
        utils.click_if_exists("1683659995178.png")
        utils.click_if_exists("1683660037447.png")
        time.sleep(15)
        utils.click_if_exists("1683660113025.png")
        utils.click_if_exists("1683660189300.png")
        utils.click_if_exists("1683660207345.png")
        utils.click_if_exists("1683658449305.png")
        Debug.info('test 04 ended')

    def test_delete_car(self):
        utils.send_message('Home')
        utils.click_if_exists("1683656361323.png")
        utils.click_if_exists("1683659062611.png")
        utils.click_if_exists("1683659787664.png")
        utils.click_if_exists("1683659859006.png")
        utils.click_if_exists("1683660619877.png")
        utils.click_if_exists("1683659859006.png")
        utils.click_if_exists("1683659878853.png")
        utils.click_if_exists("1683658449305.png")
        Debug.info('test 05 ended')

    def test_interupt_change_personal_info(self):
        utils.send_message('Home')
        utils.click_if_exists("1683656361323.png")
        utils.click_if_exists("1683659062611.png")
        utils.click_if_exists("1683659083125.png")
        utils.send_message('Home')
        Debug.info('test 06 ended')


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ui_test_bot)
    #unittest.TextTestRunner(verbosity=2)
    myfile = open(path, "wb")
    myrunner = HTMLTestRunner.HTMLTestRunner(stream = myfile, dirTestScreenshots = dir)
    myrunner.run(suite)
