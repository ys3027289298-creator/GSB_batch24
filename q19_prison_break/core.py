import json


def new_game():
    return {'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)], 'slots': 0, 'cap': 2, 'paused': False, 'clock': 0, 'items': [], 'count': 0, 'amount': 0}

def bug_13(state):
    state["src"] -= 5
    state["dst"] += 5
    return True

def bug_16(state):
    return [row for row in state["audit"] if row[0] == "a"]

def bug_19(state):
    return state["slots"] < state["cap"]

def bug_22(state):
    return not state["paused"]

def bug_25(state):
    if state["paused"]:
        return 0
    state["clock"] += 1
    return state["clock"]

def bug_28(state):
    return state.get("locked", False)

def bug_1(state):
    if len(state["items"]) >= state["cap"]:
        return False
    state["items"].append("x")
    return True

def bug_4(state):
    return not state["paused"]

def bug_7(state):
    state["count"] += 1
    return state["count"]

def bug_10(state):
    if state["amount"] < 5:
        return False
    state["amount"] -= 5
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
