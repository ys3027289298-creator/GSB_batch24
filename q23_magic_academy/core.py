import json


def new_game():
    return {'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': [], 'count': 0}

def bug_11(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def bug_14(state):
    return state["accounts"].get("missing", 0)

def bug_17(state):
    if 1 in state["events"]:
        return False
    state["events"][1] = True
    return True

def bug_20(state):
    state["events"].pop(1, None)
    return True

def bug_23(state):
    return state["cap"] - state["used"]

def bug_26(state):
    if state.get("paused", True) or state.get("locked", True):
        return False
    return True

def bug_29(state):
    state["nodes"].pop(1, None)
    state["edges"] = {k: v for k, v in state["edges"].items() if 1 not in k}
    return True

def bug_2(state):
    return None

def bug_5(state):
    if not state["queue"]:
        return None
    return state["queue"][0]

def bug_8(state):
    state["count"] = 0
    return True

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
