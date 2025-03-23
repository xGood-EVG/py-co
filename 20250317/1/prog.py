import cowsay
from io import StringIO
import shlex
import cmd
import socket
import sys
import json


WEAPONS_LIST = {"sword": 10, "spear": 15, "axe": 20}
dflt_wpn = "sword"


jgsbat = cowsay.read_dot_cow(StringIO("""
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\'--'//__
         (((""`  `"")))
"""))



class Field:

    def __init__(self, x, y):
        self._x, self._y = x, y
        self.field = list([0 for i in range(self._x)] for j in range(self._y))
        self.monsters_dict = {}

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    def addmon(self, x, y, hp, name, msg):
        self.monsters_dict[name] = self.monsters_dict.get(name, 0) + 1
        x, y = int(x), int(y)
        self.field[x][y] = Monster(x, y, hp, name, msg)


class Player:

    direct_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

    def __init__(self, field):
        self._x, self._y = 0, 0
        self.fld = field

    def move(self, direction):
        self._x, self._y = (self._x + self.__class__.direct_map[direction][0]) % self.fld.x, (self._y + self.__class__.direct_map[direction][1]) % self.fld.y
       msg = f"Moved to ({self._x}, {self._y})\n"
       if self.fld.field[self._x][self._y]:
            msg += f"Found {self.fld.field[self._x][self._y].name} {self.fld.field[self._x][self._y]._msg}\n"
        conn.send(msg.encode())


    def attack(self, name, damage):
        if self.fld.field[self._x][self._y] and self.fld.field[self._x][self._y].name == name:
            result = self.fld.field[self._x][self._y].attacked(int(damage))
            if result:
                del self.fld.field[self._x][self._y]
            return
        conn.send(f"No {name} here\n".encode())
        return


def encounter(x, y, field):
    field[x][y].greet()


class Monster:

    def __init__(self, x, y, hp, name, msg, func=None):
        self._x, self._y, self.name, self._msg, self._func = int(x), int(y), name, msg, func
        self._hp = int(hp)
        conn.send((json.dumps(fld.monsters_dict)+"\n" + f"Added monster {name} to ({x}, {y}) saying {msg}\n").encode())
        if self._func is None:
            if name == "jgsbat":
                self._func = lambda x : print(cowsay.cowsay(x, cowfile=jgsbat))
            else:
                self._func = lambda x : print(cowsay.cowsay(x, cow=name))

    def greet(self):
        self._func(self._msg)

    def __bool__(self):
        return True

    def attacked(self, damage):
        msg = f"Attacked {self.name}, damage {min(damage, self._hp)}\n"
        self._hp -= min(damage, self._hp)
        if self._hp == 0:
            msg += f"{self.name} died\n"
            conn.send(msg.encode())
            return True
        else:
            msg += f"{self.name} now has {self._hp}\n"
            conn.send(msg.encode())
            return False


if __name__ == "__main__":
    fld = Field(10, 10)
    plr = Player(fld)
    host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            conn.sendall(f"{10} {10}".encode())
            print('Connected by', addr)
            while data := conn.recv(1024):
                info = shlex.split(data.decode())
                print(info)
                if info[0] == "move":
                    plr.move(info[1])
                if info[0] == "addmon":
                    fld.addmon(*info[1:])
                if info[0] == "attack":
                    info[2] = int(info[2])
                    plr.attack(*info[1:])