import json

MAX_ACTIVE_PITS = 1
WATER_PER_REGISTRATION = 10


def new_game():
    return {'events': {1: (5, 6), 2: (1, 2)}, 'queue': [], 'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False}

def bug_24(state):
    return len(state["events"])

def bug_27(state):
    return bool(state["dst"])

def bug_0(state):
    processed = state.setdefault("processed", [])
    artifact_id = state["next_id"]
    if artifact_id in processed:
        return False
    processed.append(artifact_id)
    return True

def bug_3(state):
    if not state["queue"]:
        return None
    return state["queue"].pop(0)

def bug_6(state):
    if not state["items"]:
        return None
    return state["items"][-1]

def bug_9(state):
    artifact_id = state["next_id"]
    state["next_id"] += 1
    return artifact_id

def bug_12(state):
    if state["src"] < WATER_PER_REGISTRATION:
        return False
    state["src"] -= WATER_PER_REGISTRATION
    state["dst"] += WATER_PER_REGISTRATION
    return True

def bug_15(state):
    return not state["closed"]

def bug_18(state):
    if len(state["events"]) >= MAX_ACTIVE_PITS:
        return False
    pit_id = state["next_id"]
    state["next_id"] += 1
    state["events"][pit_id] = (0, 0)
    return True

def bug_21(state):
    return bool(state["queue"])

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
