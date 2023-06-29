
import unittest
from unittest.mock import patch, Mock

import sys
sys.path.insert(0, 'C:/Users/miror/OneDrive/Документи/Fernando codes/CarMaintanceServiceChatbot/CarMaintanceServiceChatbot/')

import sqlite3
import credentials
import services
import appointments
from appointments import display_apps
from unittest.mock import MagicMock, patch


class TestAppointments(unittest.TestCase):
    @patch('appointments.sqlite3.connect')
    @patch('appointments.contacts.user_info')
    def test_app_info(self, mock_user_info, mock_connect):
        # setup
        user_id = 1
        mock_user_info.return_value = {'user_id': user_id, 'appointments': []}
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, '2023-01-01', 'comment', 'photo', 1, 1, 1)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # call function
        result = appointments.app_info(user_id)

        # assert calls
        mock_connect.assert_called_once_with("supercar.db")
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with('SELECT * FROM appointments WHERE user = ?',(user_id, ))
        mock_cursor.fetchall.assert_called_once()
        mock_user_info.assert_called_once_with(user_id)

        # assert result
        self.assertEqual(result, {
            'user_id': user_id,
            'appointments': [
                {
                    'app_id': 1,
                    'app_date': '2023-01-01',
                    'comments': 'comment',
                    'photo': 'photo',
                    'service': 1,
                    'user': 1,
                    'car': 1
                }
            ]
        })

if __name__ == '__main__':
    unittest.main()