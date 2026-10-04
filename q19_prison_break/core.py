import json


def new_game():
    return {'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)], 'slots': 0, 'cap': 2, 'paused': False, 'clock': 0, 'items': [], 'count': 0, 'amount': 0}

def bug_13(state):
    if state["dst"] or state["src"] < 5:
        return False
    state["src"] -= 5
    state["dst"] += 5
    return True

def bug_16(state):
    audit = state["audit"]
    if not audit:
        return []
    first = min(row[1] for row in audit)
    return [row for row in audit if row[1] == first]

def bug_19(state):
    return state["slots"] < state["cap"]

def bug_22(state):
    return not state["items"]

def bug_25(state):
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]

def bug_28(state):
    return bool(state.get("locked", False))

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
    had = state["amount"] != 0
    state["amount"] = 0
    return had

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
