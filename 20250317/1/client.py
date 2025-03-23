import cmd
import sys
import socket
import shlex
import json


WEAPONS_LIST = {"sword": 10, "spear": 15, "axe": 20}
dflt_wpn = "sword"
MONSTER_DICT = {}


class cmd_line(cmd.Cmd):

    def __init__(self, sock):
        self.socket = sock
        super().__init__()

    prompt = "(MUD) "

    def do_up(self, args):
        self.socket.send("move up".encode())
        #plr.move("up")
    
    def do_down(self, args):
        self.socket.send("move down".encode())
        #plr.move("down")
    
    def do_left(self, args):
        self.socket.send("move left".encode())
        #plr.move("left")
    
    def do_right(self, args):
        self.socket.send("move right".encode())
        #plr.move("right")
    
    def do_addmon(self, args):
        global MONSTER_DICT
        name, *rules = shlex.split(args)
        try:
            hello_ind = rules.index("hello")
            hp_ind = rules.index("hp")
            coords_ind = rules.index("coords")
            x, y = int(rules[coords_ind+1]), int(rules[coords_ind+2])
            hp = int(rules[hp_ind+1])
            hello = rules[hello_ind+1]
        except:
            print("Invalid arguments")
        self.socket.sendall(f"addmon {x} {y} {hp} {name} {hello}")
        MONSTER_DICT = json.loads(self.socket.recv(1024).decode())
        #fld.addmon(x, y, hp, name, hello)
    
    def do_attack(self, args):
        try:
            name = shlex.split(args)[0]
        except:
            print("Invalid command")
            return
        if "with" in args:
            try:
                name, _, weapon = shlex.split(args)
                if WEAPONS_LIST.get(weapon, None) is None:
                    print("Unknown weapon")
                    return
                self.socket.send(f"attack {name} {WEAPONS_LIST[weapon]}")
                #plr.attack(name, WEAPONS_LIST[weapon])
            except ValueError:
                print("Need to specify the weapon")
                return
        else:
            self.socket.send(f"attack {name} {WEAPONS_LIST[dflt_wpn]}")
            #plr.attack(name, WEAPONS_LIST[dflt_wpn])
    
    def complete_attack(self, text, line, ind1, ind2):
        words = shlex.split(line)
        if len(words) == 2:
            return [c for c in MONSTER_DICT.keys() if MONSTER_DICT[c] > 0 and c.startswith(text)]
        if len(words) < 3:
            return []
        if len(words) == 3:
            return WEAPONS_LIST.keys()
        return [c for c in WEAPONS_LIST.keys() if c.startswith(text)]

if __name__ == "__main__":
    print("<<< Welcome to Python-MUD 0.1 >>>")
    host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        cmd_line(sock=s).cmdloop()
