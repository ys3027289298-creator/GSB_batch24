import json


def new_game():
    return {'slots': 0, 'cap': 2, 'paused': False, 'clock': 0, 'items': [], 'count': 0, 'amount': 0, 'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)]}

def bug_19(state):
    return True

def bug_22(state):
    return False

def bug_25(state):
    state["clock"] += 1
    return state["clock"]

def bug_28(state):
    return True

def bug_1(state):
    state["items"].append("x")
    return True

def bug_4(state):
    return True

def bug_7(state):
    state["count"] += 2
    return state["count"]

def bug_10(state):
    state["amount"] += -5
    return True

def bug_13(state):
    state["src"] -= 5
    return True

def bug_16(state):
    return state["audit"]

def main():
    print("命令: run/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
