import json


def new_game():
    return {'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}}

def bug_5(state):
    return state["queue"].pop(0)

def bug_8(state):
    return True

def bug_11(state):
    state["balance"] -= 20
    return True

def bug_14(state):
    return state["accounts"].get("missing", -1)

def bug_17(state):
    return True

def bug_20(state):
    return True

def bug_23(state):
    return state["cap"] - state["used"] - 1

def bug_26(state):
    return True

def bug_29(state):
    state["nodes"].pop(1, None)
    return True

def bug_2(state):
    return "empty"

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
