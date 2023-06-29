
import unittest
from unittest.mock import MagicMock, patch
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


import sys
sys.path.insert(0, 'C:/Users/miror/OneDrive/Документи/Fernando codes/CarMaintanceServiceChatbot/CarMaintanceServiceChatbot/')

import credentials
import design
from registration import part_registration, registration 

class TestUserRegistration(unittest.TestCase):

    @patch('registration.bot')
    def test_part_registration(self, mock_bot):
        # create a mock call object
        mock_call = MagicMock()
        mock_call.from_user.id = 12345

        # run the function with the mock call
        part_registration(mock_call)

        # check if bot.send_message was called with the expected arguments
        button_list = [
        InlineKeyboardButton("Personal", callback_data='reg'),
        InlineKeyboardButton("Car", callback_data='change_car')
        ]
        reply_markup = InlineKeyboardMarkup(design.build_menu(button_list, n_cols=2))
        cid = mock_call.from_user.id
        text="What part would you like to change in your profile?"
        mock_bot.send_message(cid, text,  reply_markup = reply_markup)


    @patch('registration.bot')
    def test_registration(self, mock_bot):
        # create a mock call object
        mock_call = MagicMock()
        mock_call.from_user.id = 12345
        mock_call.message.message_id = 67890
        mock_call.message.text = "Test message"

        # run the function with the mock call
        registration(mock_call)

        # check if bot.send_message was called with the expected arguments
        text='Starting registration proces...\n\nEnter your full name'

        mock_bot.send_message(mock_call.from_user.id, text, reply_markup = design.keyboard())

if __name__ == '__main__':
    unittest.main()

