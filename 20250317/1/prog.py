import cowsay
from io import StringIO
import shlex
import cmd


WEAPONS_LIST = {"sword": 10, "spear": 15, "axe": 20}
dflt_wpn = "sword"


class cmd_line(cmd.Cmd):

    prompt = "(MUD) "

    def do_up(self, args):
        plr.move("up")
    
    def do_down(self, args):
        plr.move("down")
    
    def do_left(self, args):
        plr.move("left")
    
    def do_right(self, args):
        plr.move("right")
    
    def do_addmon(self, args):
        name, *rules = shlex.split(args)
        try:
            hello_ind = rules.index("hello")
            hp_ind = rules.index("hp")
            coords_ind = rules.index("coords")
            x, y = int(rules[coords_ind+1]), int(rules[coords_ind+2])
            hp = int(rules[hp_ind+1])
            hello = rules[hello_ind]
        except:
            print("Invalid arguments")
        fld.addmon(x, y, hp, name, hello)
    
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
                plr.attack(name, WEAPONS_LIST[weapon])
            except ValueError:
                print("Need to specify the weapon")
                return
        else:
            plr.attack(name, WEAPONS_LIST[dflt_wpn])
    
    def complete_attack(self, text, line, ind1, ind2):
        words = shlex.split(line)
        if len(words) == 2:
            return [c for c in fld.monsters_dict.keys() if fld.monsters_dict[c] > 0 and c.startswith(text)]
        if len(words) < 3:
            return []
        if len(words) == 3:
            return WEAPONS_LIST.keys()
        return [c for c in WEAPONS_LIST.keys() if c.startswith(text)]


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
        try:
            x, y = int(x), int(y)
        except:
            print("Invalid arguments")
            return
        if x < 0 or y < 0 or x >= self.x or y >= self.y or not (hasattr(msg, "__str__") or hasattr(msg, "__repr__")):
            print("Invalid arguments")
            return
        if name not in [*cowsay.list_cows(), "jgsbat"]:
            print("Cannot add unknown monster")
            return
        self.monsters_dict[name] = self.monsters_dict.get(name, 0) + 1
        self.field[x][y] = Monster(x, y, hp, name, msg)


class Player:

    direct_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

    def __init__(self, field):
        self._x, self._y = 0, 0
        self.fld = field

    def move(self, direction):
        self._x, self._y = (self._x + self.__class__.direct_map[direction][0]) % self.fld.x, (self._y + self.__class__.direct_map[direction][1]) % self.fld.y
        print(f"Moved to ({self._x}, {self._y})")
        if self.fld.field[self._x][self._y]:
            encounter(self._x, self._y, self.fld.field)

    def attack(self, name, damage):
        if self.fld.field[self._x][self._y] and self.fld.field[self._x][self._y].name == name:
            result = self.fld.field[self._x][self._y].attacked(damage)
            if result:
                del self.fld.field[self._x][self._y]
            return
        print(f"No {name} here")
        return


def encounter(x, y, field):
    field[x][y].greet()


class Monster:

    def __init__(self, x, y, hp, name, msg, func=None):
        self._x, self._y, self.name, self._msg, self._func = x, y, name, msg, func
        self._hp = hp
        print(f"Added monster {name} to ({x}, {y}) saying {msg}")
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
        print(f"Attacked {self.name}, damage {min(damage, self._hp)}")
        self._hp -= min(damage, self._hp)
        if self._hp == 0:
            print(f"{self.name} died")
            return True
        else:
            print(f"{self.name} now has {self._hp}")
            return False



if __name__ == "__main__":
    fld = Field(10, 10)
    plr = Player(fld)
    print("<<< Welcome to Python-MUD 0.1 >>>")
    cmd_line().cmdloop()
