import shutil
import os

def cleaner():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("po"):
        shutil.rmtree("po")
    print("Finished cleaning")

def task_html():
    return {
        'actions': ["make html"],
        'file_dep': ["Makefile"],
        'targets': ["build"],
        'clean': [cleaner]
    }

def task_test():
    return {
        'actions': ["python3 -m unittest"],
        'file_dep': ["test_client.py", "test_server.py"]
    }

def task_update():
    return {
        'actions': [
            "mkdir po",
            "mkdir po/ru_RU.UTF-8",
            "mkdir po/ru_RU.UTF-8/LC_MESSAGES",
            "pybabel update -D mood_lang -d po -i mood_lang.pot --init-missing -l ru_RU.UTF-8"
        ],
        'file_dep': ["mood_lang.pot"],
        'targets': ["po/ru_RU.UTF-8/LC_MESSAGES/mood_lang.po"]
    }

def task_compile():
    return {
        'actions': ["pybabel compile -D mood_lang -d po -l ru_RU.UTF-8"],
        'file_dep': ["po/ru_RU.UTF-8/LC_MESSAGES/mood_lang.po"],
        'targets': ["po/ru_RU.UTF-8/LC_MESSAGES/mood_lang.mo"]
    }
