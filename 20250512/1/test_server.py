import multiprocessing.process
import unittest
import multiprocessing
import socket
import time
from mood.server import *


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.proc = multiprocessing.Process(target=start_server, args=(1332,))
        cls.proc.start()
        time.sleep(2)
        cls.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.socket.connect(("localhost", 1332))
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.proc.terminate()
        return super().tearDownClass()

    def test_0_login(self):
        self.socket.sendall("login".encode())
        time.sleep(1)
        resp = self.socket.recv(1024).decode().split('\n')
        print(resp)
        correct = ["User login logged in", "srv user login login", "srv fieldsz ", "srv existing monsters "]
        self.assertEqual(True, all([y.startswith(x) for x, y in zip(correct, resp)]))

    def test_1_move_off(self):
        self.socket.sendall("movemonsters off".encode())
        resp = self.socket.recv(1024).decode().rstrip('\n')
        self.assertEqual(resp, "Moving monsters: off")

    def test_2_addmon(self):
        self.socket.sendall("addmon 1 0 10 dragon hello".encode())
        time.sleep(1)
        resp = self.socket.recv(1024).decode().split('\n')
        correct = ["User login added monster dragon to (1, 0) saying hello",
                   "srv added monster dragon", ""]
        self.assertEqual(correct, resp)
    
    def test_3_encounter(self):
        self.socket.sendall("move right".encode())
        resp = self.socket.recv(1024).decode().split("\n")
        correct = ["Moved to (1, 0)", "Found dragon", "srv found dragon hello", ""]
        self.assertEqual(correct, resp)

    def test_4_attack(self):
        self.socket.sendall("attack dragon 10".encode())
        resp = self.socket.recv(1024).decode().split('\n')
        correct = ["User login attacked dragon, damage 10", "dragon died", "srv died monster dragon", ""]
        self.assertEqual(resp, correct)
