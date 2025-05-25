import json

tr_dict = {"ru_RU": {
        "Moved to ({x}, {y})": "Перемещение в ({x}, {y})",
        "Found {name} {msg}": "Found {name} {msg}",
        "No {name} here": "Здесь нет {name}",
        "User {login} added monster {name} to ({x}, {y}) saying {msg}": "Игрок {login} добавил монстра {name} в поле ({x}, {y}) говорящего {msg}",
        "User {login} attacked {name}, damage {dmg}": "Игрок {login} атаковал {name}, урон {dmg}",
        "{name} died": "{name} умер",
        "{name} now has {hp}": "{name} теперь имеет {hp} хп",
        "{name} moved one cell {dir}": "{name} переместился на одну клетку {dir}",
        "Login already in use!": "Логин уже используется!",
        "User {login} logged in": "Игрок {login} подключился",
        "Moving monsters: {state}": "Перемещения монстров: {state}",
        "Set locale: {loc}": "Установлена локаль: {loc}",
        "User {login} left the game": "Игрок {login} покинул игру"
    }
}


def translate(msg, locale):
    tr = tr_dict[locale].get(msg, None)
    if tr is None:
        print("Message {msg} isn't supported in {locale} translation".format(msg=msg, locale=locale))
        return ""
    return tr
