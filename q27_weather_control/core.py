import json

# ---------------------------------------------------------------------------
# 天气控制站统一状态模型
#
# 一个控制站状态只包含四类东西：
#   编号    : next_id          下一条天气指令的编号（先取号、再自增）
#   能源    : src/dst/items    src 为容量上限，dst 为已产出能源，
#                              items 是逐次执行留下的能源流水，dst 永远等于
#                              len(items)，能源数量只有这一份事实来源
#   运行态  : closed/queue/events
#             closed 为暂停/锁定；queue 是按进入顺序处理的 FIFO 队列；
#             events 是待查看的天气指令 id -> (优先级, ...)
#   幂等台账: _seen            已处理过的指令/步骤，防止同一条指令或同一次
#                              执行被重复记账
#
# 所有入口都经过同一套流程：_ensure 修复（含损坏状态恢复）-> 守卫（暂停、
# 容量、空队列、重复处理）-> 变更，任何一条不满足都返回空值/False，且状态
# 不发生部分修改。创建、推进、回滚、读档共用同一份结构与同一份校验。
# ---------------------------------------------------------------------------

INITIAL_ENERGY = 5


def _blank():
    """一份全新的、可直接 json 序列化的状态。"""
    return {
        'next_id': 1,
        'src': INITIAL_ENERGY,
        'dst': 0,
        'closed': False,
        'events': {},
        'queue': [],
        'items': [],
        '_seen': {},
    }


def new_game():
    """创建：每次都是独立的新状态。"""
    return _blank()


def _ensure(state):
    """把任意传入值修复成合法状态；无法修复时返回 None。

    覆盖失败路径：非 dict、缺字段、字段类型损坏、编号非法等，全部就地
    补默认值而不是抛异常。
    """
    if not isinstance(state, dict):
        return None
    blank = _blank()
    for key, default in blank.items():
        if key not in state or state[key] is None:
            state[key] = type(default)() if isinstance(default, (dict, list)) else default

    if not isinstance(state['next_id'], int) or isinstance(state['next_id'], bool):
        state['next_id'] = 1
    if not isinstance(state['src'], int) or isinstance(state['src'], bool):
        state['src'] = INITIAL_ENERGY
    if not isinstance(state['dst'], int) or isinstance(state['dst'], bool):
        state['dst'] = 0
    state['closed'] = bool(state.get('closed'))
    if not isinstance(state['events'], dict):
        state['events'] = {}
    if not isinstance(state['queue'], list):
        state['queue'] = []
    if not isinstance(state['items'], list):
        state['items'] = []
    if not isinstance(state['_seen'], dict):
        state['_seen'] = {}

    # 能源账实核对：dst 只允许是流水长度，杜绝重复累计/少算一后的漂移。
    state['dst'] = len(state['items'])
    if state['next_id'] < 1:
        state['next_id'] = 1
    return state


# ------------------------- 创建 / 推进 / 回滚 / 读档 -------------------------

def allocate_id(state):
    """取号：返回当前编号并自增。先给号后推进，读档恢复 next_id 后不跳号。"""
    state = _ensure(state)
    if state is None:
        return None
    command_id = state['next_id']
    state['next_id'] = command_id + 1
    return command_id


def _once(state, token):
    """幂等台账：同一 token 只允许生效一次，重复请求一律 False。"""
    if state['_seen'].get(token):
        return False
    state['_seen'][token] = True
    return True


def _current_token(state):
    """当前队首天气指令的身份；队列空时用哨兵 0。"""
    return state['queue'][0] if state['queue'] else 0


def can_advance(state):
    """推进前的统一守卫：未锁定、有等待指令、控制塔未满。"""
    state = _ensure(state)
    if state is None:
        return False
    if state['closed']:
        return False
    if not state['queue']:
        return False
    if len(state['items']) >= state['src']:
        return False
    return True


def advance(state):
    """推进一次：取队首指令执行，成功记一笔能源；重复调用不会重复记账。"""
    state = _ensure(state)
    if state is None:
        return False
    if state['closed']:
        return False
    if not state['queue']:
        return False
    if len(state['items']) >= state['src']:
        return False
    command_id = state['queue'][0]
    if not _once(state, 'cmd:%s' % (command_id,)):
        return False
    state['queue'].pop(0)
    state['items'].append(command_id)
    state['dst'] = len(state['items'])
    return True


def rollback(state):
    """回滚：重置/读档时必须清空已累计能源，恢复初始容量与空流水。"""
    state = _ensure(state)
    if state is None:
        return None
    state['src'] = INITIAL_ENERGY
    state['dst'] = 0
    state['items'] = []
    return state


def save_game(state):
    state = _ensure(state)
    if state is None:
        return None
    return json.dumps(state)


def load_game(raw):
    """读档：解析失败/结构损坏时回退到新游戏，绝不保留半份旧状态。"""
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return new_game()
    if not isinstance(data, dict):
        return new_game()
    state = _ensure(data)
    # 编号恢复：存档损坏（<=0/非整数）时按现存最大编号续号，避免跳号。
    existing = [i for i in list(state['events'].keys()) + list(state['queue'])
                if isinstance(i, int) and not isinstance(i, bool)]
    floor_id = max(existing) + 1 if existing else 1
    if state['next_id'] < floor_id:
        state['next_id'] = floor_id
    state['_seen'] = {}
    return state


# ------------------------------ 命令入口（名称不变） ------------------------------

def bug_9(state):
    # 读档后编号跳号：先返回当前编号再自增。
    return allocate_id(state)


def bug_12(state):
    # 重置/读档没有清空能源：恢复初始容量并清空累计值。
    return rollback(state) is not None


def bug_15(state):
    # 暂停或锁定状态仍执行：锁定即拒绝。
    state = _ensure(state)
    return state is not None and not state['closed']


def bug_18(state):
    # 同一条天气指令重复处理：队首指令只处理一次，第二次返回 False。
    state = _ensure(state)
    if state is None:
        return False
    return _once(state, 'weather:%s' % (_current_token(state),))


def bug_21(state):
    # 控制塔达到上限后仍继续执行：统一推进守卫（同时挡住空队列与锁定）。
    return can_advance(state)


def bug_24(state):
    # 查看天气指令：只读优先级最高（元组首项最小）的一条，不删除。
    state = _ensure(state)
    if state is None or not state['events']:
        return None
    valid = ((cid, info) for cid, info in state['events'].items()
             if isinstance(info, (list, tuple)) and info)
    try:
        return min(valid, key=lambda item: item[1][0])[0]
    except ValueError:
        return None


def bug_27(state):
    # 空控制塔操作：没有内容时返回 None，而不是占位文本。
    state = _ensure(state)
    if state is None or not state['items']:
        return None
    return state['items'][0]


def bug_0(state):
    # 单次执行重复累计能源：同一步骤只记账一次。
    state = _ensure(state)
    if state is None:
        return False
    if state['closed'] or len(state['items']) >= state['src']:
        return False
    if not _once(state, 'step:%s' % (_current_token(state),)):
        return False
    state['items'].append(len(state['items']) + 1)
    state['dst'] = len(state['items'])
    return True


def bug_3(state):
    # 先进入的天气指令先处理：从队首弹出 FIFO。
    state = _ensure(state)
    if state is None or not state['queue']:
        return None
    return state['queue'].pop(0)


def bug_6(state):
    # 能源数量少算一：流水多长就是多少，不再 -1。
    state = _ensure(state)
    if state is None:
        return 0
    return len(state['items'])


def main():
    print("命令: run/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        if raw == "run":
            print("ok" if advance(state) else "")


if __name__ == "__main__":
    main()
