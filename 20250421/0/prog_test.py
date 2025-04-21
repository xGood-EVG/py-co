import unittest
import prog
import prognet
import socket
import multiprocessing

class TestProg(unittest.TestCase):

    def test_0_sqroots(self):
        self.assertEqual(prog.sqroots("1 2 1"), "-1.0")

    def test_1_sqroots(self):
        self.assertEqual(prog.sqroots("1 1 1"), "")

    def test_2_sqroots(self):
        self.assertEqual(prog.sqroots("1 -5 6"), "3.0 2.0")

    def test_3_sqroots(self):
        with self.assertRaises(ZeroDivisionError):
            prog.sqroots("0 1 1")


class TestPrognet(unittest.TestCase):

    def setUp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect()

