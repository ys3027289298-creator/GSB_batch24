import json


def new_game():
    return {'paused': False, 'clock': 0, 'items': [], 'cap': 2, 'count': 0, 'amount': 0, 'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)], 'slots': 0}

def bug_22(state):
    return state["amount"] >= 0 and state["src"] >= 0 and state["dst"] >= 0

def bug_25(state):
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]

def bug_28(state):
    if state["amount"] <= 0:
        return None
    amount = state["amount"]
    state["amount"] = 0
    return amount

def bug_1(state):
    if len(state["items"]) >= state["cap"]:
        return False
    state["items"].append("x")
    return True

def bug_4(state):
    if state["paused"]:
        return False
    return True

def bug_7(state):
    state["count"] += 1
    return state["count"]

def bug_10(state):
    if state["amount"] < 5:
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
    if not state["audit"]:
        return []
    key = state["audit"][0][0]
    return [row for row in state["audit"] if row[0] == key]

def bug_19(state):
    if state["slots"] >= state["cap"]:
        return False
    state["slots"] += 1
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
