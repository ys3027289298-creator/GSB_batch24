import json


def new_game():
    return {'paused': False, 'locked': False, 'count': 0, 'amount': 0, 'src': 10, 'dst': 0, 'audit': [('a', 1), ('b', 2)], 'slots': 0, 'cap': 2, 'clock': 0, 'items': []}


def _active(state):
    return not state.get('paused', False) and not state.get('locked', False)


def bug_4(state):
    return _active(state)


def bug_7(state):
    if not _active(state):
        return state.get('count', 0)
    state['count'] = state.get('count', 0) + 1
    return state['count']


def bug_10(state):
    amount = state.get('amount', 0)
    if amount < 5:
        return False
    state['amount'] = amount - 5
    return True


def bug_13(state):
    if not _active(state):
        return False
    src = state.get('src', 0)
    if src < 5:
        return False
    state['src'] = src - 5
    state['dst'] = state.get('dst', 0) + 5
    return True


def bug_16(state, key='a'):
    return [row for row in state.get('audit', []) if row[0] == key]


def bug_19(state):
    return state.get('slots', 0) < state.get('cap', 0)


def bug_22(state):
    state['count'] = 0
    return True


def bug_25(state):
    if not _active(state):
        return state.get('clock', 0)
    state['clock'] = state.get('clock', 0) + 1
    return state['clock']


def bug_28(state, target='x'):
    if not _active(state):
        return None
    items = state.get('items', [])
    if not items:
        return None
    return items.pop(0)


def bug_1(state, target='x'):
    if not _active(state):
        return False
    items = state.setdefault('items', [])
    if len(items) >= state.get('cap', 0):
        return False
    if target in items:
        return False
    items.append(target)
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
