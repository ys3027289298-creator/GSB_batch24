import json


def _save(state):
    return json.dumps({
        "events": state["events"],
        "queue": state["queue"],
        "next_id": state["next_id"],
        "src": state["src"],
        "dst": state["dst"],
    })


def _restore(state, save):
    data = json.loads(save)
    events = {}
    for rid, value in data.get("events", {}).items():
        events[int(rid)] = tuple(value)
    state["events"] = events
    state["queue"] = list(data.get("queue", []))
    state["next_id"] = int(data.get("next_id", 1))
    state["src"] = int(data.get("src", 0))
    state["dst"] = int(data.get("dst", 0))
    state["items"] = []
    state["processed"] = []


def new_game():
    state = {
        'events': {1: (5, 6), 2: (1, 2)},
        'queue': [],
        'items': [],
        'next_id': 1,
        'src': 5,
        'dst': 0,
        'closed': False,
        'paused': False,
        'cap': 100,
        'processed': [],
        'history': [],
    }
    state['history'] = [_save(state)]
    return state


def _oldest(state):
    events = state.get("events") or {}
    if not events:
        return None
    return min(events, key=lambda rid: events[rid][0])


def bug_21(state):
    return state["dst"] >= state["cap"]


def bug_24(state):
    return _oldest(state)


def bug_27(state):
    rid = _oldest(state)
    return rid is not None and rid in state["processed"]


def bug_0(state):
    rid = _oldest(state)
    if rid is None or rid in state["processed"]:
        return False
    state["history"].append(_save(state))
    state["processed"].append(rid)
    return True


def bug_3(state):
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def bug_6(state):
    return len(state["items"])


def bug_9(state):
    rid = state["next_id"]
    state["next_id"] += 1
    return rid


def bug_12(state):
    if not bug_15(state) or bug_21(state):
        return False
    if state["src"] < 10:
        return False
    state["history"].append(_save(state))
    state["src"] -= 10
    state["dst"] += 10
    state["items"].append(1)
    return True


def bug_15(state):
    return not state.get("closed", False) and not state.get("paused", False)


def bug_18(state):
    if not state["history"]:
        return False
    save = state["history"].pop()
    try:
        _restore(state, save)
    except (ValueError, TypeError, KeyError):
        return False
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
