import json


def new_game():
    return {'src': 5, 'dst': 0, 'closed': False, 'events': {}, 'queue': [], 'items': [], 'next_id': 1, 'processed': [], 'recorded': False}

def bug_12(state):
    amount = 10
    if state["src"] < amount:
        return False
    state["src"] -= amount
    state["dst"] += amount
    return True

def bug_15(state):
    if state.get("closed"):
        return False
    return True

def bug_18(state):
    if state.get("recorded"):
        return False
    state["recorded"] = True
    return True

def bug_21(state):
    if not state["items"]:
        return None
    return state["items"][-1]

def bug_24(state):
    if not state["events"]:
        return None
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def bug_27(state):
    if state["dst"] == 0:
        return False
    state["dst"] = 0
    return True

def bug_0(state):
    processed = state.setdefault("processed", [])
    clue = state["queue"][0] if state["queue"] else None
    if clue in processed:
        return False
    processed.append(clue)
    return True

def bug_3(state):
    if not state["queue"]:
        return None
    return state["queue"].pop(0)

def bug_6(state):
    return len(state["items"])

def bug_9(state):
    nid = state["next_id"]
    state["next_id"] += 1
    return nid

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
