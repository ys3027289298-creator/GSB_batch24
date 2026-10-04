import json


def new_game():
    return {'slots': 0, 'cap': 2, 'paused': False, 'clock': 0, 'items': [], 'count': 0, 'amount': 0, 'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)]}

def bug_19(state):
    return state["slots"] < state["cap"]

def bug_22(state):
    return True

def bug_25(state):
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]

def bug_28(state):
    return False

def bug_1(state):
    if len(state["items"]) >= state["cap"]:
        return False
    if "x" in state["items"]:
        return False
    state["items"].append("x")
    return True

def bug_4(state):
    return not state["paused"]

def bug_7(state):
    state["count"] += 1
    return state["count"]

def bug_10(state):
    if state["amount"] <= 0:
        return False
    state["amount"] -= 5
    return True

def bug_13(state):
    if state["src"] < 5:
        return False
    state["src"] -= 5
    state["dst"] += 5
    return True

def bug_16(state):
    return [row for row in state["audit"] if row[0] == "a"]

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
