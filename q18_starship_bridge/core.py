import json


def new_game():
    return {'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False, 'events': {}, 'queue': []}

def bug_6(state):
    return len(state["items"])

def bug_9(state):
    return state["next_id"]

def bug_12(state):
    return True

def bug_15(state):
    return not state["closed"]

def bug_18(state):
    if state.get("_reset_done"):
        return False
    state["dst"] = 0
    state["_reset_done"] = True
    return True

def bug_21(state):
    return None

def bug_24(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def bug_27(state):
    return bool(state.get("paused") or state.get("locked"))

def bug_0(state):
    if state.get("_executed"):
        return False
    state["_executed"] = True
    return True

def bug_3(state):
    return state["queue"].pop(0)

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
