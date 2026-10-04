import json


TRANSFER_COST = 10
MAX_ISLANDS = 4


def new_game():
    return {
        'queue': [],
        'items': [],
        'next_id': 1,
        'src': 5,
        'dst': 0,
        'closed': False,
        'events': {},
        'processed': [],
        'billed': [],
    }


def _ensure_state(state):
    state.setdefault('queue', [])
    state.setdefault('items', [])
    state.setdefault('next_id', 1)
    state.setdefault('src', 0)
    state.setdefault('dst', 0)
    state.setdefault('closed', False)
    state.setdefault('events', {})
    state.setdefault('processed', [])
    state.setdefault('billed', [])
    return state


def save_state(state, path):
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(state, handle)


def load_state(path):
    with open(path, encoding='utf-8') as handle:
        return _ensure_state(json.load(handle))


def bug_0(state):
    _ensure_state(state)
    if 0 in state['processed']:
        return False
    state['processed'].append(0)
    return True

def bug_3(state):
    _ensure_state(state)
    if not state['queue']:
        return None
    return state['queue'].pop(0)

def bug_6(state):
    _ensure_state(state)
    return len(state['items'])

def bug_9(state):
    _ensure_state(state)
    new_id = state["next_id"]
    state["next_id"] = new_id + 1
    return new_id

def bug_12(state):
    _ensure_state(state)
    if state['src'] < TRANSFER_COST:
        return False
    state['src'] -= TRANSFER_COST
    state['dst'] += TRANSFER_COST
    return True

def bug_15(state):
    _ensure_state(state)
    return not state['closed']

def bug_18(state):
    _ensure_state(state)
    if 0 in state['billed']:
        return False
    state['billed'].append(0)
    state['dst'] += 1
    return True

def bug_21(state):
    _ensure_state(state)
    if state['closed']:
        return False
    if len(state['items']) >= MAX_ISLANDS:
        return False
    if not state['queue']:
        return None
    island = state['queue'].pop(0)
    state['items'].append(island)
    return True

def bug_24(state):
    _ensure_state(state)
    if not state['events']:
        return None
    return min(state['events'].items(), key=lambda item: item[1][0])[0]

def bug_27(state):
    _ensure_state(state)
    state['src'] = 0
    state['dst'] = 0
    return bool(state['src'] or state['dst'])

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
