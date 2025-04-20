"""Server side of MOOD"""


import random
import cowsay
import shlex
import socket
import sys
import json
import threading
import os
import time
import functools
from mood.common import translation

DIRECTIONS = {"up": (0, -1), "down": (0, 1),
                  "left": (-1, 0), "right": (1, 0)}
WEAPONS_LIST = {"sword": 10, "spear": 15, "axe": 20}
ALL_MONSTERS = list()
dflt_wpn = "sword"
FIELDX, FIELDY = 10, 10
MOVE = "on"

LOCALES = {
    "ru_RU": functools.partial(translation.translate, locale="ru_RU"),
    "en_EN": lambda x: x
}

def translate(msg, locale, fmt):
    msg = "\n".join(LOCALES[locale](x).format(**fmt) if not x.startswith("srv") else x for x in msg.split("\n"))
    return msg

with open(os.path.join("mood", "common", "bat.txt")) as f:
    jgsbat = cowsay.read_dot_cow(f)

class Communicator():
    """Class for managing connected users and sending them messages"""

    def __init__(self):
        """Initiation of communication manager"""
        self.logins = dict()  # addr -> login
        self.connections = dict()  # login -> socket
        self.locales = dict()  # socket -> locale

    def add_connection(self, conn, addr, login):
        """This runs when a new user is connected to send him messages"""
        self.logins[addr] = login
        self.connections[login] = conn
        self.locales[conn] = "en_EN"

    def remove_connection(self, addr):
        """This runs when users disconnect to delete him from message subscribers"""
        login = self.logins[addr]
        del self.logins[addr]
        del self.locales[self.connections[login]]
        del self.connections[login]

    def sendall(self, msg: str, fmt: dict):
        """Sends given message to all logined users"""
        for _, conn in self.connections.items():
            conn.sendall(translate(msg, self.locales[conn], fmt).encode())

    def send(self, conn: socket.socket, msg: str, fmt: dict):
        """Sends given message to given socket"""
        conn.sendall(translate(msg, self.locales[conn], fmt).encode())
    
    def set_locale(self, conn, locale):
        self.locales[conn] = locale

    def player_exists(self, login: str) -> bool:
        """Check if player with specified login is still playing"""
        return True if self.connections.get(login, False) else False


class Field:
    """Class for the in-game field"""

    def __init__(self, x, y, cm):
        """Initiating field instance"""
        self._x, self._y = x, y
        self.monsters = list([0 for i in range(self._x)] for j in range(self._y))
        self.players = list([[] for i in range(self._x)] for j in range(self._y))
        self.monsters_dict = {}
        self.cm = cm

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
        self.monsters[x][y] = Monster(x, y, hp, name, msg, plr, self, self.cm)


class Player:
    """Class for player"""

    def __init__(self, field, login, cm):
        """Creating player instance with start coords and login"""
        self._x, self._y = 0, 0
        self.fld = field
        field.players[self._x][self._y].append(self)
        self.login = login
        self.cm = cm
        self.locale = "en_EN"

    def move(self, direction, conn):
        """Move in a given direction"""
        self.fld.players[self._x][self._y].remove(self)
        self._x = (self._x
                   + DIRECTIONS[direction][0]) % self.fld.x
        self._y = (self._y
                   + DIRECTIONS[direction][1]) % self.fld.y
        self.fld.players[self._x][self._y].append(self)
        fmt = {"x": self._x, "y": self._y}
        msg = "Moved to ({x}, {y})\n"
        if self.fld.monsters[self._x][self._y]:
            name = self.fld.monsters[self._x][self._y].name
            fmt.update({"name": name, "msg": self.fld.monsters[self._x][self._y]._msg})
            msg += "Found {name} {msg}\n"
        self.cm.send(conn, msg, fmt)

    def attack(self, name, damage, conn):
        """Attack a monster, located in the same cell with the player"""
        if self.fld.monsters[self._x][self._y] and \
                self.fld.monsters[self._x][self._y].name == name:
            result = self.fld.monsters[self._x][self._y].attacked(
                int(damage), self.login
            )
            if result:
                del self.fld.monsters[self._x][self._y]
            return
        self.cm.send(conn, "No {name} here\n", {"name": name})
        return

    def sayall(self, *msg):
        """Send message to all users"""
        self.cm.sendall("{login}: {msg}", {"login": self.login,
                                                "msg": ' '.join(msg)})


class Monster:
    """Class representing mosters"""

    def __init__(self, x, y, hp, name, msg, plr, fld, cm, func=None):
        """
        Initializing monster, need to provide his hp,
        coords, name and message, which will appear, when
        players meet him
        """
        self.author = plr
        self._x, self._y, self.name = int(x), int(y), name
        self._msg, self._func = msg, func
        self._hp = int(hp)
        self.fld = fld
        self.cm = cm
        ALL_MONSTERS.append(self)
        cm.sendall(
          "User {login} added monster {name} to ({x}, {y}) saying {msg}\n",
            {
                "login": plr.login,
                "name": name,
                "x": x,
                "y": y,
                "msg": msg
            }
        )
        cm.sendall("srv added monster {name}\n", {"name": name})
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
        fmt = {
            "login": login,
            "name": self.name,
            "dmg": dmg
        }
        msg = "User {login} attacked {name}, damage {dmg}\n"
        self._hp -= min(damage, self._hp)
        if self._hp == 0:
            msg += "{name} died\n"
            msg += "srv died monster {name}\n"
            self.fld.monsters[self._x][self._y] = 0
            self.fld.monsters_dict[self.name] -= 1
            ALL_MONSTERS.remove(self)
            self.cm.sendall(msg, fmt)
            return True
        else:
            fmt.update({"hp": self._hp})
            msg += "{name} now has {hp}\n"
            self.cm.sendall(msg, fmt)
            return False

    def move(self, dir):
        """Function that moves monster in a chosen direction, if there is no monster in the next cell"""
        next_x, next_y = (self._x + DIRECTIONS[dir][0]) % self.fld.x, (self._y + DIRECTIONS[dir][1]) % self.fld.y
        if not self.fld.monsters[next_x][next_y]:
            self.fld.monsters[self._x][self._y] = 0
            self.cm.sendall("{name} moved one cell {dir}\n", {
                "name": self.name,
                "dir": dir
            })
            self._x, self._y = next_x, next_y
            self.fld.monsters[self._x][self._y] = self
            for pl in self.fld.players[self._x][self._y]:
                self.cm.send(self.cm.connections[pl.login], "Found {name} {msg}\n", {
                    "name": self.name,
                    "msg": self._msg
                })
            return True
        return False


def handler(conn, addr, cm, fld):
    """This runs for each client to process his actions"""
    global MOVE
    with conn:
        print('Connected by', addr)
        login = conn.recv(1024).decode()
        if cm.player_exists(login):
            conn.send("Login already in use!\n".encode())
            return
        cm.add_connection(conn, addr, login)
        cm.sendall("User {login} logged in\n", {"login": login})
        cm.send(conn, "srv user login {login}\n".format(login=login), {})
        cm.send(conn, "srv fieldsz {x} {y}\n".format(x=FIELDX, y=FIELDY), {})
        monsters = json.dumps(fld.monsters_dict)
        cm.send(conn, "srv existing monsters {monsters}\n".format(monsters=monsters), {})
        plr = Player(fld, login, cm)
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
            if info[0] == "movemonsters":
                MOVE = info[1]
                cm.sendall("Moving monsters: {state}\n", {"state": info[1]})
            if info[0] == "locale":
                cm.set_locale(conn, info[1])
                cm.send(conn, "Set locale: {loc}\n", {"loc": info[1]})
        cm.remove_connection(addr)
        cm.sendall("User {login} left the game\n", {"login": login})
        cm.sendall("srv user left {login}".format(login=login), {})


def random_move():
    """Moves random monster in a random direction every thirty seconds"""
    while True:
        time.sleep(30)
        if not ALL_MONSTERS or MOVE == "off":
            continue
        while not random.choice(ALL_MONSTERS).move(random.choice(list(DIRECTIONS.keys()))):
            continue