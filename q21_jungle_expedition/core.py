import json

TRANSFER_AMOUNT = 10

_FIELD_TYPES = {
    'queue': list,
    'items': list,
    'processed': list,
    'events': dict,
    'next_id': int,
    'src': int,
    'dst': int,
    'closed': bool,
    'active': bool,
}


def _defaults():
    return {
        'queue': [],
        'items': [],
        'processed': [],
        'events': {},
        'next_id': 1,
        'src': 5,
        'dst': 0,
        'closed': False,
        'active': True,
    }


def new_game():
    """创建：返回一份完整、合法的新状态。"""
    return _defaults()


def _is_bad(key, value):
    expected = _FIELD_TYPES[key]
    if isinstance(value, bool) and expected is not bool:
        return True
    if not isinstance(value, expected):
        return True
    if key == 'next_id' and value < 1:
        return True
    if key in ('src', 'dst') and value < 0:
        return True
    return False


def _is_corrupt(state):
    if not isinstance(state, dict):
        return True
    return any(key not in state or _is_bad(key, state[key]) for key in _FIELD_TYPES)


def _normalize(state):
    """损坏状态恢复：缺失或非法的字段重置为默认值。"""
    for key, default in _defaults().items():
        if key not in state or _is_bad(key, state[key]):
            state[key] = default
    return state


def _known_ids(state):
    ids = []
    entries = list(state['queue']) + list(state['items']) + list(state['processed']) + list(state['events'])
    for value in entries:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            ids.append(value)
        elif isinstance(value, str) and value.isdigit():
            ids.append(int(value))
    return ids


def save_game(state):
    _normalize(state)
    return json.dumps(state)


def load_game(payload):
    """读档：解析并规范化状态，修复编号使其不与已有补给冲突。"""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        data = None
    state = new_game()
    if isinstance(data, dict):
        for key, value in data.items():
            if key in state:
                state[key] = value
    _normalize(state)
    ids = _known_ids(state)
    if ids and state['next_id'] <= max(ids):
        state['next_id'] = max(ids) + 1
    return state


def bug_0(state):
    """推进：处理当前补给；同一补给重复处理时返回 False。"""
    _normalize(state)
    supply_id = state['next_id']
    if supply_id in state['processed']:
        return False
    state['processed'].append(supply_id)
    return True


def bug_3(state):
    """按先进先出顺序取出队首补给；空队列返回 None。"""
    _normalize(state)
    if not state['queue']:
        return None
    return state['queue'].pop(0)


def bug_6(state):
    """统计营地已分配补给的数量。"""
    _normalize(state)
    return len(state['items'])


def bug_9(state):
    """发放当前编号后再自增，保证编号连续不跳号。"""
    _normalize(state)
    supply_id = state['next_id']
    state['next_id'] = supply_id + 1
    return supply_id


def bug_12(state):
    """单次定量转运水源；锁定或存量不足时失败且不改动状态。"""
    _normalize(state)
    if state['closed'] or state['src'] < TRANSFER_AMOUNT:
        return False
    state['src'] -= TRANSFER_AMOUNT
    state['dst'] += TRANSFER_AMOUNT
    return True


def bug_15(state):
    """暂停或锁定状态下拒绝执行分配。"""
    _normalize(state)
    return not state['closed']


def bug_18(state):
    """回滚/重置：清空水源记录并转为非活动状态，重复调用幂等。"""
    _normalize(state)
    if not state['active']:
        return False
    state['events'] = {}
    state['dst'] = 0
    state['active'] = False
    return True


def bug_21(state):
    """查看营地最近分配的补给；空营地返回 None，且不移除。"""
    _normalize(state)
    if not state['items']:
        return None
    return state['items'][-1]


def bug_24(state):
    """查看储量最小的水源编号，只查看不移除；无水源返回 None。"""
    _normalize(state)
    if not state['events']:
        return None
    return min(state['events'].items(), key=lambda item: (item[1][0], item[0]))[0]


def bug_27(state):
    """完整性检查：状态损坏（缺字段或类型非法）时返回 True。"""
    return _is_corrupt(state)


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
