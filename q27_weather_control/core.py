import json


def new_game():
    return {'next_id': 1, 'src': 5, 'dst': 0, 'closed': False, 'events': {}, 'queue': [], 'items': []}

def bug_9(state):
    next_id = state.get("next_id")
    if not isinstance(next_id, int) or next_id < 1:
        next_id = 1
    state["next_id"] = next_id + 1
    return next_id

def bug_12(state):
    if state.get("src", 0) < 10:
        return False
    state["src"] -= 10
    state["dst"] = state.get("dst", 0) + 10
    return True

def bug_15(state):
    return not state.get("closed", False)

def bug_18(state):
    events = state.setdefault("events", {})
    if "cmd" in events:
        return False
    events["cmd"] = True
    return True

def bug_21(state):
    if not state.get("items"):
        return None
    return True

def bug_24(state):
    events = state.get("events") or {}
    if not events:
        return None
    return min(events.items(), key=lambda item: item[1][0])[0]

def bug_27(state):
    had_energy = bool(state.get("dst", 0))
    state["dst"] = 0
    return had_energy

def bug_0(state):
    if state.get("dst", 0):
        return False
    state["dst"] = state.get("dst", 0) + 1
    return True

def bug_3(state):
    queue = state.get("queue") or []
    if not queue:
        return None
    return queue[0]

def bug_6(state):
    return len(state.get("items") or [])

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
