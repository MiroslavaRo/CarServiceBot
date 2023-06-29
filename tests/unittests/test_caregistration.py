
import unittest
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, 'C:/Users/miror/OneDrive/Документи/Fernando codes/CarMaintanceServiceChatbot/CarMaintanceServiceChatbot/')

import credentials
import design
import caregistration  # Change this to the actual module name

class TestCarRegistration(unittest.TestCase):
    
    @patch('caregistration.bot')
    def test_car_registration(self, mock_bot):
        # Set up the mock bot object
        mock_bot.send_message = MagicMock()
        
        # Mock message
        mock_msg = MagicMock()
        mock_msg.chat.id = 1
        mock_msg.message_id = 1
        mock_msg.text = "Test message"

        # Call the function
        caregistration.car_registration(mock_msg)

        # Check that the bot's send_message method was called with the expected arguments     
        mock_bot.send_message(mock_msg.chat.id, "How would you like to register your car?", reply_markup = design.keyboard())
        mock_bot.send_message(mock_msg.chat.id, "How would you like to register your car?", reply_markup = caregistration.car_reg_buttons())

    @patch('caregistration.bot')
    @patch('caregistration.car_dict')
    def test_process_brand_step(self, mock_car_dict, mock_bot):
        # Set up the mock bot and car_dict objects
        mock_bot.reply_to = MagicMock()
        mock_car_dict.__getitem__.return_value = MagicMock()

        # Mock message
        mock_msg = MagicMock()
        mock_msg.chat.id = 1
        mock_msg.text = "Test brand"

        # Call the function
        caregistration.process_brand_step(mock_msg)

        # Check that the bot's reply_to method was called with the expected arguments
        mock_bot.reply_to.assert_called_with(mock_msg, 'Enter model of your car')

if __name__ == '__main__':
    unittest.main()
