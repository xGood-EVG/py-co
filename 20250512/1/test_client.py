import unittest
from unittest import mock
# import io
# import sys
from mood.client import *


class TestClient(unittest.TestCase):

    def test_0_up(self):
        with (
            mock.patch('socket.socket', autospec=True) as sock,
            mock.patch('mood.client.receiver', return_value=True)
        ):
            start_client(file_="./testing/test_0.txt")
            send = sock.mock_calls[4].args[0]
            self.assertEqual(send, b'move up')

    def test_1_down(self):
        with (
            mock.patch('socket.socket', autospec=True) as sock,
            mock.patch('mood.client.receiver', return_value=True)
        ):
            start_client(file_="./testing/test_1.txt")
            send = sock.mock_calls[4].args[0]
            self.assertEqual(send, b'move down')

    def test_2_addmon(self):
        with (
            mock.patch('socket.socket', autospec=True) as sock,
            mock.patch('mood.client.receiver', return_value=True)
        ):
            start_client(file_="./testing/test_2.txt")
            send = sock.mock_calls[4].args[0]
            print(send)
            self.assertEqual(send, b'addmon 1 1 15 dragon hello')

    def test_4_addmon(self):
        with (
            mock.patch('socket.socket', autospec=True) as sock,
            mock.patch('mood.client.receiver', return_value=True)
        ):
            start_client(file_="./testing/test_3.txt")
            send = sock.mock_calls[4].args[0]
            print(send)
            self.assertNotEqual(send, b'addmon 1 1 15 dragon hello')
