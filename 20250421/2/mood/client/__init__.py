"""Client side of MOOD"""


import cmd
import socket
import shlex
import json
import cowsay
import readline
import threading
from argparse import ArgumentParser
import time

WEAPONS_LIST = {"sword": 10, "spear": 15, "axe": 20}
dflt_wpn = "sword"
MONSTER_DICT = {}
LOGINED_USERS = set()
field_x, field_y = 100, 100


def encounter(name, msg):
    """This happens when you meet a monster"""
    print(cowsay.cowsay(msg, cow=name))
    print(cmd_line.prompt, end="", flush=True)


class MessageParser():
    """Class for parsing incoming messages"""

    @classmethod
    def parse(cls, data: str):
        """Parse upcoming message"""
        for msg in data.split('\n'):
            if not msg:
                continue
            if not msg.startswith("srv"):
                print(f"{msg}\n{cmd_line.prompt if cmd_line.use_rawinput else ''}{readline.get_line_buffer()}",
                      end="",
                      flush=True)
                if msg.startswith("Found"):
                    encounter(*msg.split()[1:])
            else:
                cmd = msg.split()
                match cmd:
                    case ["srv", "fieldsz", *xy]:
                        global field_x, field_y
                        x, y = xy
                        field_x, field_y = int(x), int(y)
                    case ["srv", "existing", "monsters", *x]:
                        global MONSTER_DICT
                        MONSTER_DICT = json.loads(" ".join(x))
                    case ["srv", "added", "monster", name]:
                        MONSTER_DICT[name] = MONSTER_DICT.get(name, 0) + 1
                    case ["srv", "died", "monster", name]:
                        MONSTER_DICT[name] -= 1


class cmd_line(cmd.Cmd):
    """Shell for the game"""

    def __init__(self, sock, *args, **kwargs):
        """Initialize socket for sending messages"""
        self.socket = sock
        def timeout(): return
        if kwargs.get('stdin', None):
            self.__class__.use_rawinput = False
            def timeout(): time.sleep(1)
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    prompt = "(MUD) "    

    def do_up(self, args):
        """Move up"""
        self.socket.send("move up".encode())

    def do_down(self, args):
        """Move down"""
        self.socket.send("move down".encode())

    def do_left(self, args):
        """Move left"""
        self.socket.send("move left".encode())

    def do_right(self, args):
        """Move right"""
        self.socket.send("move right".encode())

    def do_sayall(self, args):
        """Send message for all users"""
        self.socket.send(("sayall "+args).encode())
    
    def do_movemonsters(self, args):
        """Turn on/off the monsters movements"""
        if args not in ["on", "off"]:
            print(args, "is not valid")
            return
        self.socket.send(("movemonsters "+args).encode())

    def do_locale(self, args):
        """Change locale"""
        if args not in ["ru_RU", "en_EN"]:
            print(args, "is not valid")
            return
        self.socket.send(("locale "+args).encode())

    def postcmd(self, stop: bool, line: str) -> bool:
        self.timeout()
        return super().postcmd(stop, line)
    
    def postloop(self):
        return 1

    def do_addmon(self, args):
        """
        Add a monster with given attributes, required are name, coordinates,
        message and hp
        """
        try:
            name, *rules = shlex.split(args)
            hello_ind = rules.index("hello")
            hp_ind = rules.index("hp")
            coords_ind = rules.index("coords")
            x, y = int(rules[coords_ind+1]), int(rules[coords_ind+2])
            hp = int(rules[hp_ind+1])
            hello = rules[hello_ind+1]
        except Exception:
            print("Invalid arguments")

        if name not in [*cowsay.list_cows(), "jgsbat"]:
            print("Cannot add unknown monster")
            return
        if x < 0 or y < 0 or x >= field_x or y >= field_y or \
                not (hasattr(hello, "__str__") or hasattr(hello, "__repr__")):
            print("Invalid arguments")
            return
        self.socket.sendall(f"addmon {x} {y} {hp} {name} {hello}".encode())

    def do_attack(self, args):
        """Attack the monster in the player's cell with weapon, if specified"""
        try:
            name = shlex.split(args)[0]
        except Exception:
            print("Invalid command")
            return
        if "with" in args:
            try:
                name, _, weapon = shlex.split(args)
                if WEAPONS_LIST.get(weapon, None) is None:
                    print("Unknown weapon")
                    return
                self.socket.send(
                    f"attack {name} {WEAPONS_LIST[weapon]}".encode()
                )
            except ValueError:
                print("Need to specify the weapon")
                return
        else:
            self.socket.send(
                f"attack {name} {WEAPONS_LIST[dflt_wpn]}".encode()
            )

    def complete_attack(self, text, line, ind1, ind2):
        """Autocomplete for function attack"""
        words = shlex.split(line)
        if len(words) == 2:
            return [c for c in MONSTER_DICT.keys()
                    if MONSTER_DICT[c] > 0 and c.startswith(text)]
        if len(words) < 3:
            return []
        if len(words) == 3:
            return WEAPONS_LIST.keys()
        return [c for c in WEAPONS_LIST.keys() if c.startswith(text)]
    
    def do_EOF(self, args):
        """When EOF"""
        return 1


def receiver(conn):
    """Function, running in a different thread to receive messages"""
    while data := conn.recv(1024):
        MessageParser.parse(data.decode())

def start_client(login="login", file_=""):
    parser = ArgumentParser()
    parser.add_argument("login", default=login, action="store", nargs="?")
    parser.add_argument("port", action="store",
                        default=1337, type=int, nargs='?')
    parser.add_argument("host", action="store",
                        default="localhost", nargs='?')
    parser.add_argument("--file",
                        default=file_)
    args = parser.parse_args()
    print(args.login)
    print("<<< Welcome to Python-MUD 0.1 >>>")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        s.send(args.login.encode())
        recv = threading.Thread(target=receiver, args=(s, ))
        recv.start()
        if args.file:
            with open(args.file) as f:
                cmd_line(sock=s, stdin=f).cmdloop()
        else:
            cmd_line(sock=s).cmdloop()
        s.shutdown(socket.SHUT_RDWR)
    recv.join()