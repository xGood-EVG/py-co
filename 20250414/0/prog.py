from collections import Counter
import gettext
import os
import locale

#locale.setlocale(locale.LC_ALL, ("ru_RU", "UTF-8"))
os.environ["language"] = "ru_RU"

translation = gettext.translation("WCount", "po", fallback=True)
_, ngettext = translation.gettext, translation.ngettext

while True:
    n = len(list(Counter(input().split()).keys()))
    print(ngettext("Entered {n} word", "Entered {n} words", n).format(n=n))
