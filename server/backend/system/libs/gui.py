"""
# Register or enter in system
UNKNOWN-> register

# Enter you login, password and name
LOGIN------> login
PASSWORD---> password
NAME-------> name

# Success
# Register or enter in system
UNKNOWN-> enter

LOGIN------> login
PASSWORD---> password

# Success
NAME-> new_chat

INTERLOCUR-> ^user
CHAT_NAME--> Chat

# Success
NAME-> choose_chat

CHAT_NAME--> Chat

# Success
NAME:CHAT-> Message
NAME:CHAT-> Message

NAME:CHAT-> /exit
NAME-> ...
"""

"""
...
Interlocur: Message
You: Meesage
Intercolur: Message
Intercolur: Message

NAME:CHAT-> Meesage
"""




"""
> register
enter


REGISTER
> login   : ...
password  : 
name      :


ENTER
> login   : ...
password  : ...
"""


def goto (x: int, y: int):
    try:
        print(f'\033[{y}:{x}H', end='')
    except Exception:
        raise

def go_up (n: int):
    try:
        print(f'\033[{n}A', end='')
    except Exception:
        raise

def go_down (n: int):
    try:
        print(f'\033[{n}B', end='')
    except Exception:
        raise

def go_left (n: int):
    try:
        print(f'\033[{n}D', end='')
    except Exception:
        raise

def go_right (n: int):
    try:
        print(f'\033[{n}C', end='')
    except Exception:
        raise

def save_position ():
    try:
        print('\033[s', end='')
    except Exception:
        raise

def load_position ():
    try:
        print('\033[u', end='')
    except Exception:
        raise