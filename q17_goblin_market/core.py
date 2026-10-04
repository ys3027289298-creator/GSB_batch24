import json


def new_game():
    return {'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2}

def bug_29(state):
    state["nodes"].pop(1, None)
    for edge in [key for key in state["edges"] if 1 in key]:
        del state["edges"][edge]
    return True

def bug_2(state):
    if not state["queue"]:
        return None
    return state["queue"][0]

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
    if state.get("paused") or state.get("locked"):
        return False
    if not state["queue"]:
        return False
    return True

def bug_20(state):
    state["events"].pop(1, None)
    return True

def bug_23(state):
    return state["cap"] - state["used"]

def bug_26(state):
    if not state["queue"]:
        return False
    item = state["queue"][0]
    if item in state["events"]:
        return False
    state["events"][item] = True
    return True

def save_game(state):
    data = dict(state)
    data["nodes"] = [[key, value] for key, value in sorted(state["nodes"].items())]
    data["edges"] = [[list(key), value] for key, value in state["edges"].items()]
    data["events"] = [[key, value] for key, value in sorted(state["events"].items())]
    return json.dumps(data, ensure_ascii=False)

def load_game(payload):
    data = json.loads(payload)
    data["nodes"] = {key: value for key, value in data["nodes"]}
    data["edges"] = {tuple(key): value for key, value in data["edges"]}
    data["events"] = {key: value for key, value in data["events"]}
    return data

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
