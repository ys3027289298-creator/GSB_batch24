import json


def new_game():
    return {'closed': False, 'events': {}, 'queue': [], 'items': [], 'next_id': 1, 'src': 5, 'dst': 0}


def _normalize(state):
    if not isinstance(state.get('closed'), bool):
        state['closed'] = bool(state.get('closed', False))
    if not isinstance(state.get('events'), dict):
        state['events'] = {}
    else:
        events = {}
        for key, value in state['events'].items():
            try:
                events[int(key)] = value
            except (TypeError, ValueError):
                continue
        state['events'] = events
    for key in ('queue', 'items'):
        if not isinstance(state.get(key), list):
            state[key] = []
    if not isinstance(state.get('next_id'), int) or state['next_id'] < 1:
        state['next_id'] = 1
    for key, default in (('src', 5), ('dst', 0)):
        if not isinstance(state.get(key), (int, float)):
            state[key] = default
    if not isinstance(state.get('processed'), set):
        state['processed'] = set()
    if state['events']:
        state['next_id'] = max(state['next_id'], max(state['events']) + 1)
    return state


def load_game(payload):
    if isinstance(payload, (str, bytes)):
        try:
            payload = json.loads(payload)
        except (ValueError, TypeError):
            payload = None
    state = dict(payload) if isinstance(payload, dict) else new_game()
    _normalize(state)
    _reset_transient(state)
    return state


def _reset_transient(state):
    state['items'] = []
    state['processed'].clear()


def _once(state, token):
    if token in state['processed']:
        return False
    state['processed'].add(token)
    return True


def _transfer(state, amount):
    if amount <= 0 or state['src'] < amount:
        return False
    state['src'] -= amount
    state['dst'] += amount
    return True


def bug_15(state):
    _normalize(state)
    return not state['closed']


def bug_18(state):
    _normalize(state)
    return _once(state, 'advance')


def bug_21(state):
    _normalize(state)
    return list(state['items'])


def bug_24(state):
    _normalize(state)
    if not state['events']:
        return None
    return min(state['events'].items(), key=lambda item: item[1][0])[0]


def bug_27(state):
    _normalize(state)
    _reset_transient(state)
    return bool(state['items'])


def bug_0(state):
    _normalize(state)
    return _once(state, 'hunt')


def bug_3(state):
    _normalize(state)
    if not state['queue']:
        return None
    return state['queue'].pop(0)


def bug_6(state):
    _normalize(state)
    return len(state['items'])


def bug_9(state):
    _normalize(state)
    next_id = state['next_id']
    state['next_id'] = next_id + 1
    return next_id


def bug_12(state):
    _normalize(state)
    return _transfer(state, 10)


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
