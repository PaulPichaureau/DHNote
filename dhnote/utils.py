import pinyin
import re

H1regexp = re.compile(r"^#\s(.*)\n")


def hanzi2name(h, format="diacritical"):
    if len(h) != 4:
        return pinyin.get(h, delimiter="", format=format)
    p = pinyin.get(h, delimiter=" ", format=format).split(" ")
    name = ""
    for i in range(0, len(p), 2):
        name += p[i] + p[i + 1] + " "
    return name.strip().title()


def map_listorstring(f, x, **kwargs):
    if isinstance(x, str):
        return f(x, **kwargs)
    elif isinstance(x, list):
        return [f(_, **kwargs) for _ in x]
    return x


def first_defined_in_dict(d, l):
    for k in l:
        if k in d and d[k] is not None:
            return d[k]
    return None
