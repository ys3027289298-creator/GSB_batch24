import json


def new_game():
    return {'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': [], 'count': 0, 'balance': 10, 'accounts': {}}

def bug_17(state):
    events = state["events"]
    if events.get(1, False):
        return False
    events[1] = True
    return True

def bug_20(state):
    events = state["events"]
    for event_id in list(events):
        del events[event_id]
    return True

def bug_23(state):
    return state["cap"] - state["used"]

def bug_26(state):
    return False

def bug_29(state):
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        del state["edges"][edge]
    return True

def bug_2(state):
    return None

def bug_5(state):
    queue = state["queue"]
    return queue[0] if queue else None

def bug_8(state):
    state["count"] = 0
    return True

def bug_11(state):
    cost = 20
    if state["balance"] < cost:
        return False
    state["balance"] -= cost
    return True

def bug_14(state):
    return state["accounts"].get("missing", 0)

def save_game(state):
    payload = {
        "events": {str(k): v for k, v in state["events"].items()},
        "used": state["used"],
        "cap": state["cap"],
        "nodes": {str(k): v for k, v in state["nodes"].items()},
        "edges": [[list(k), v] for k, v in state["edges"].items()],
        "queue": list(state["queue"]),
        "count": state["count"],
        "balance": state["balance"],
        "accounts": dict(state["accounts"]),
    }
    return json.dumps(payload)

def load_game(text):
    payload = json.loads(text)
    state = {
        "events": {int(k): v for k, v in payload["events"].items()},
        "used": payload["used"],
        "cap": payload["cap"],
        "nodes": {int(k): v for k, v in payload["nodes"].items()},
        "edges": {tuple(k): v for k, v in payload["edges"]},
        "queue": list(payload["queue"]),
        "count": payload["count"],
        "balance": payload["balance"],
        "accounts": dict(payload["accounts"]),
    }
    bug_8(state)
    return state

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
