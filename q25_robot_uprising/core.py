import json


def new_game():
    return {'paused': False, 'clock': 0, 'items': [], 'cap': 2, 'count': 0, 'amount': 0, 'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)], 'slots': 0}


def save_state(state):
    return json.dumps(state, separators=(',', ':'), sort_keys=True)


def load_state(blob):
    state = json.loads(blob)
    state['audit'] = [tuple(row) for row in state.get('audit', [])]
    return state


def bug_25(state):
    if state.get('paused'):
        return state['clock']
    state['clock'] += 1
    return state['clock']


def bug_28(state):
    if state.get('paused'):
        return None
    items = state['items']
    if not items:
        return None
    unit = items.pop(0)
    if state['slots'] > 0:
        state['slots'] -= 1
    return unit


def bug_1(state):
    if state.get('paused'):
        return False
    unit = 'x'
    items = state['items']
    if len(items) >= state['cap'] or state['slots'] >= state['cap']:
        return False
    if unit in items:
        return False
    items.append(unit)
    state['slots'] += 1
    return True


def bug_4(state):
    if state.get('paused'):
        return False
    if not state['items']:
        return False
    if state['slots'] >= state['cap']:
        return False
    return True


def bug_7(state):
    state['count'] += 1
    return state['count']


def bug_10(state):
    if state['amount'] < 5:
        return False
    state['amount'] -= 5
    return True


def bug_13(state):
    if state.get('src', 0) < 5:
        return False
    state['src'] -= 5
    state['dst'] += 5
    return True


def bug_16(state):
    items = state['items']
    target = items[0] if items else 'a'
    return [tuple(row) for row in state['audit'] if tuple(row)[0] == target]


def bug_19(state):
    if state.get('paused'):
        return False
    return state['slots'] < state['cap']


def bug_22(state):
    fresh = new_game()
    for key in ('paused', 'clock', 'items', 'count', 'amount', 'src', 'dst', 'audit', 'slots'):
        state[key] = fresh[key]
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
