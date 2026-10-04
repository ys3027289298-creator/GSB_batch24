import json


def new_game():
    return {'events': {}, 'queue': [], 'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False, 'cared': False, 'processed': False}

def bug_18(state):
    if state.get("processed"):
        return False
    state["processed"] = True
    return True

def bug_21(state):
    return state["dst"] >= state["src"]

def bug_24(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def bug_27(state):
    if not state["queue"]:
        return None
    return state["queue"][0]

def bug_0(state):
    if state.get("cared"):
        return False
    state["cared"] = True
    return True

def bug_3(state):
    return state["queue"][0]

def bug_6(state):
    return len(state["items"])

def bug_9(state):
    egg_id = state["next_id"]
    state["next_id"] += 1
    return egg_id

def bug_12(state):
    state["dst"] = 0
    return True

def bug_15(state):
    return not state["closed"]

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
