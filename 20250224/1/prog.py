import cowsay


class Field:

    def __init__(self, x, y):
        self._x, self._y = x, y
        self.field = list([0 for i in range(self._x)] for j in range(self._y))

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    def addmon(self, x, y, msg):
        try:
            x, y = int(x), int(y)
        except:
            print("Invalid arguments")
            return
        if x < 0 or y < 0 or x >= self.x or y >= self.y or not (hasattr(msg, "__str__") or hasattr(msg, "__repr__")):
            print("Invalid arguments")
            return
        self.field[x][y] = Monster(x, y, msg)


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


def encounter(x, y, field):
    field[x][y].greet()


class Monster:

    def __init__(self, x, y, msg, func=lambda x : print(cowsay.cowsay(x))):
        self._x, self._y, self._msg, self._func = x, y, msg, func

    def greet(self):
        self._func(self._msg)

    def __bool__(self):
        return True


if __name__ == "__main__":
    fld = Field(10, 10)
    plr = Player(fld)
    while (s := input()):
        match s.split():
            case ["addmon", x, y, msg]:
                fld.addmon(x, y, msg)
            case ["up" | "down" | "left" | "right"] as cmd:
                plr.move(*cmd)
            case _:
                print("Invalid command")
