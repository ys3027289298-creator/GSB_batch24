import json


def new_game():
    return {'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}}

def bug_23(state):
    return state["cap"] - state["used"]

def bug_26(state):
    return state["used"] >= state["cap"]

def bug_29(state):
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        del state["edges"][edge]
    return True

def bug_2(state):
    return None

def bug_5(state):
    return state["queue"][0] if state["queue"] else None

def bug_8(state):
    state["count"] = 0
    return True

def bug_11(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def bug_14(state):
    return state["accounts"].get("missing", 0)

def bug_17(state):
    return False

def bug_20(state):
    state["events"].pop(1, None)
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
