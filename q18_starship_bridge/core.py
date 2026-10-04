import json

CONSOLE_CAPACITY = 1
TRANSFER_COST = 10


def new_game():
    return {'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False, 'events': {}, 'queue': []}


def check_invariants(state):
    assert state["next_id"] >= 1
    assert state["src"] >= 0
    assert len(state["queue"]) <= CONSOLE_CAPACITY
    return True


def save_game(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def load_game(state, path):
    with open(path, "r", encoding="utf-8") as fh:
        saved = json.load(fh)
    state.clear()
    state.update(saved)
    check_invariants(state)
    return state


def bug_0(state):
    command_id = state["next_id"]
    if command_id in state["events"]:
        return False
    state["events"][command_id] = (command_id, 0)
    return True


def bug_3(state):
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_6(state):
    return len(state["items"])


def bug_9(state):
    command_id = state["next_id"]
    state["next_id"] += 1
    return command_id


def bug_12(state):
    if state["src"] < TRANSFER_COST:
        return False
    state["src"] -= TRANSFER_COST
    state["dst"] += TRANSFER_COST
    return True


def bug_15(state):
    if state["closed"]:
        return False
    return True


def bug_18(state):
    if len(state["queue"]) >= CONSOLE_CAPACITY:
        return False
    state["queue"].append(state["next_id"])
    return True


def bug_21(state):
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_24(state):
    if not state["events"]:
        return None
    return min(state["events"].items(), key=lambda item: item[1][0])[0]


def bug_27(state):
    if not state["items"]:
        return False
    state["items"] = []
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
