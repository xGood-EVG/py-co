import unittest
import prognet
import socket
import multiprocessing

proc = multiprocessing.Process(target=prognet.serve)
proc.start()

def sqrootnet(coeffs: str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())
    return s.recv(128).decode().strip()

class TestProg(unittest.TestCase):

    def test_0_sqroots(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 1337))
        self.assertEqual(sqrootnet("1 2 1", s), "-1.0")

    def test_1_sqroots(self):
        self.assertEqual(prognet.sqroots("1 1 1"), "")

    def test_2_sqroots(self):

        self.assertEqual(prognet.sqroots("1 -5 6"), "3.0 2.0")

    def test_3_sqroots(self):
        with self.assertRaises(ZeroDivisionError):
            prognet.sqroots("0 1 1")

