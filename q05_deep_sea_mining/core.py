import json


def new_game():
    return {'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}}

def bug_5(state):
    if not state["queue"]:
        return None
    return state["queue"][0]

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
    if not state["queue"]:
        return False
    state["queue"].pop(0)
    state["count"] += 1
    return True

def bug_20(state):
    if 1 not in state["events"]:
        return False
    del state["events"][1]
    return True

def bug_23(state):
    return state["cap"] - state["used"]

def bug_26(state):
    if state.get("paused", False) or state.get("locked", True):
        return False
    if not state["queue"] or state["used"] >= state["cap"]:
        return False
    state["queue"].pop(0)
    state["used"] += 1
    state["count"] += 1
    return True

def bug_29(state):
    state["nodes"].pop(1, None)
    state["edges"] = {edge: cost for edge, cost in state["edges"].items() if 1 not in edge}
    return True

def bug_2(state):
    return None

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
