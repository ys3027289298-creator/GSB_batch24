import json


NEST_CAPACITY = 3
CARE_COST = 10


def new_game():
    return {'events': {}, 'queue': [], 'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False, 'done': []}

def bug_18(state):
    if 'hatch' in state['done']:
        return False
    state['done'].append('hatch')
    return True

def bug_21(state):
    eggs = len(state['items'])
    return 0 < eggs < NEST_CAPACITY

def bug_24(state):
    return min(state["events"].items(), key=lambda item: (item[1][0], item[0]))[0]

def bug_27(state):
    if not state['items']:
        return False
    return state['items'][0]

def bug_0(state):
    if 'care' in state['done']:
        return False
    state['done'].append('care')
    return True

def bug_3(state):
    if not state["queue"]:
        return None
    return state["queue"].pop(0)

def bug_6(state):
    return len(state["items"])

def bug_9(state):
    egg_id = state["next_id"]
    state["next_id"] += 1
    return egg_id

def bug_12(state):
    if state["src"] < CARE_COST:
        return False
    state["src"] -= CARE_COST
    state["dst"] += CARE_COST
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
