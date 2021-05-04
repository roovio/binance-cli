import json

D = "D"
I = "I"
W = "W"
E = "E"


def msg(t, *args):
    print(f"{t}:", *args)

def debug(*args):
    msg(D, *args)

def info(*args):
    msg(I, *args)

def warn(*args):
    msg(W, *args)

def err(*args):
    msg(E, *args)

def pretty_json(s):
    print(json.dumps(s, indent=4, sort_keys=True))
