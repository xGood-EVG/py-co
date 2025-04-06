"""Server side of MOOD"""


import cowsay
import shlex
import socket
import sys
import json
import threading
import os


WEAPONS_LIST = {"sword": 10, "spear": 15, "axe": 20}
dflt_wpn = "sword"
FIELDX, FIELDY = 10, 10

with open(os.path.join("common", "bat.txt")) as f:
    jgsbat = cowsay.read_dot_cow(f)


class Communicator():
    """Class for managing connected users and sending them messages"""

    def __init__(self):
        """Initiation"""
        self.logins = dict()  # addr -> login
        self.connections = dict()  # login -> socket

    def add_connection(self, conn, addr, login):
        """This runs when a new user is connected"""
        self.logins[addr] = login
        self.connections[login] = conn

    def remove_connection(self, addr):
        """This runs when users disconnect"""
        login = self.logins[addr]
        del self.logins[addr]
        del self.connections[login]

    def sendall(self, msg: str):
        """Sends given message to all logined users"""
        for conn in self.connections.values():
            conn.sendall(msg.encode())

    def send(self, conn: socket.socket, msg: str):
        """Sends given message to given socket"""
        conn.sendall(msg.encode())

    def player_exists(self, login: str) -> bool:
        """Check if player with specified login is still playing"""
        return True if self.connections.get(login, False) else False


class Field:
    """Class for the in-game field"""

    def __init__(self, x, y):
        """Initiating field instance"""
        self._x, self._y = x, y
        self.field = list([0 for i in range(self._x)] for j in range(self._y))
        self.monsters_dict = {}

    @property
    def x(self):
        """Return size of x axis"""
        return self._x

    @property
    def y(self):
        """Return size of y axis"""
        return self._y

    def addmon(self, x, y, hp, name, msg, plr):
        """Create a monster and pin it to a field's cell"""
        self.monsters_dict[name] = self.monsters_dict.get(name, 0) + 1
        x, y = int(x), int(y)
        self.field[x][y] = Monster(x, y, hp, name, msg, plr)


class Player:
    """Class for player"""

    direct_map = {"up": (0, -1), "down": (0, 1),
                  "left": (-1, 0), "right": (1, 0)}

    def __init__(self, field, login):
        """Creating player instance with start coords and login"""
        self._x, self._y = 0, 0
        self.fld = field
        self.login = login

    def move(self, direction, conn):
        """Move in a given direction"""
        self._x = (self._x
                   + self.__class__.direct_map[direction][0]) % self.fld.x
        self._y = (self._y
                   + self.__class__.direct_map[direction][1]) % self.fld.y
        msg = f"Moved to ({self._x}, {self._y})\n"
        if self.fld.field[self._x][self._y]:
            name = self.fld.field[self._x][self._y].name
            msg += f"Found {name} {self.fld.field[self._x][self._y]._msg}\n"
        cm.send(conn, msg)

    def attack(self, name, damage, conn):
        """Attack a monster, located in the same cell with the player"""
        if self.fld.field[self._x][self._y] and \
                self.fld.field[self._x][self._y].name == name:
            result = self.fld.field[self._x][self._y].attacked(
                int(damage), self.login
            )
            if result:
                del self.fld.field[self._x][self._y]
            return
        cm.send(conn, f"No {name} here\n")
        return

    def sayall(self, *msg):
        """Send message to all users"""
        cm.sendall(f"{self.login}: {' '.join(msg)}")


class Monster:
    """Class representing mosters"""

    def __init__(self, x, y, hp, name, msg, plr, func=None):
        """
        Initializing monster, need to provide his hp,
        coords, name and message, which will appear, when
        players meet him
        """
        self.author = plr
        self._x, self._y, self.name = int(x), int(y), name
        self._msg, self._func = msg, func
        self._hp = int(hp)
        cm.sendall(
          f"User {plr.login} added monster {name} to ({x}, {y}) saying {msg}\n"
        )
        cm.sendall(f"srv added monster {name}\n")
        if self._func is None:
            if name == "jgsbat":
                self._func = lambda x: print(cowsay.cowsay(x, cowfile=jgsbat))
            else:
                self._func = lambda x: print(cowsay.cowsay(x, cow=name))

    def __bool__(self):
        """This is needed to check, if there's a monster in a cell"""
        return True

    def attacked(self, damage, login):
        """Function called, when monster is attacked to deal damage"""
        dmg = min(damage, self._hp)
        msg = f"User {login} attacked {self.name}, damage {dmg}\n"
        self._hp -= min(damage, self._hp)
        if self._hp == 0:
            msg += f"{self.name} died\n"
            msg += f"srv died monster {self.name}\n"
            cm.sendall(msg)
            return True
        else:
            msg += f"{self.name} now has {self._hp}\n"
            cm.sendall(msg)
            return False


def handler(conn, addr):
    """This runs for each client to process his actions"""
    with conn:
        print('Connected by', addr)
        login = conn.recv(1024).decode()
        if cm.player_exists(login):
            conn.send("Login already in use!\n".encode())
            return
        cm.add_connection(conn, addr, login)
        cm.sendall(f"User {login} logged in\n")
        cm.send(conn, f"srv user login {login}\n")
        cm.send(conn, f"srv fieldsz {FIELDX} {FIELDY}\n")
        monsters = json.dumps(fld.monsters_dict)
        cm.send(conn, f"srv existing monsters {monsters}\n")
        plr = Player(fld, login)
        while data := conn.recv(1024):
            info = shlex.split(data.decode())
            print(info)
            if info[0] == "move":
                plr.move(info[1], conn)
            if info[0] == "addmon":
                fld.addmon(*info[1:], plr)
            if info[0] == "attack":
                info[2] = int(info[2])
                plr.attack(*info[1:], conn)
            if info[0] == "sayall":
                plr.sayall(*info[1:])
    cm.remove_connection(addr)
    cm.sendall(f"User {login} left the game\n")
    cm.sendall(f"srv user left {login}")


if __name__ == "__main__":
    fld = Field(FIELDX, FIELDY)
    port = 1337 if len(sys.argv) < 2 else int(sys.argv[1])
    host = "localhost" if len(sys.argv) < 3 else sys.argv[2]
    cm = Communicator()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            client = threading.Thread(target=handler, args=(conn, addr))
            client.start()
