
import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, 'C:/Users/miror/OneDrive/Документи/Fernando codes/CarMaintanceServiceChatbot/CarMaintanceServiceChatbot/')

import contacts

class TestUserInfo(unittest.TestCase):
    @patch('sqlite3.connect')
    def test_user_info(self, mock_sqlite3_connect):
        mock_con = MagicMock()
        mock_cur = MagicMock()
        mock_sqlite3_connect.return_value = mock_con
        mock_con.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (1, 'testuser', 'Test User', '+123456789', 'testuser@example.com')
        mock_cur.fetchall.return_value = [(1, 'Tesla', 'Model S', 2022, 'Electric', None)]

        expected_result = {
            'chat_id': 1,
            'username': 'testuser',
            'full_name': 'Test User',
            'phone': '+123456789',
            'email': 'testuser@example.com',
            'carlist': [{'car_id': 1, 'brand': 'Tesla', 'model': 'Model S', 'year': 2022, 'engine': 'Electric', 'tech_passport': None}]
        }
        result = contacts.user_info(1)
        self.assertEqual(result, expected_result)


class TestContactsButns(unittest.TestCase):
    @patch('contacts.design.build_menu')
    def test_contacts_butns(self, mock_build_menu):
        mock_build_menu.return_value = [[{"text": "🚘Add car", "callback_data": "add_car"}, {"text": "⚒Change information", "callback_data": "change"}, {"text": "✍️Appointments", "callback_data": "appoitments"}]]

        expected_result = [[{"text": "🚘Add car", "callback_data": "add_car"}, {"text": "⚒Change information", "callback_data": "change"}, {"text": "✍️Appointments", "callback_data": "appoitments"}]]
        result = contacts.contacts_butns()
        self.assertEqual(result.keyboard, expected_result)


if __name__ == '__main__':
    unittest.main()
