"""避难所防守:统一的创建 / 推进 / 回滚 / 读档状态模型。

状态字段:
    queue      等候难民队列(先进先出)
    items      食物储备
    next_id    编号分配器(连续,不跳号)
    src / dst  伙食账目:待转运 / 已入库
    closed     暂停 / 锁定标记
    events     事件编号 -> (到达时间, 负载)
    cap / used 隔离间容量 / 已占用
    settled    已结算伙食(幂等台账)
    clock      到达次序时钟
    processed  幂等台账:已处理对象 / 已整备标记
"""

import copy
import json

_DEFAULTS = {
    "queue": [],
    "items": [],
    "next_id": 1,
    "src": 5,
    "dst": 0,
    "closed": False,
    "events": {},
    "cap": 2,
    "used": 0,
    "settled": 0,
    "clock": 0,
    "processed": [],
}

_LIST_FIELDS = ("queue", "items", "processed")
_INT_FIELDS = ("next_id", "src", "dst", "cap", "used", "settled", "clock")
_RESET_TOKEN = "reset"
_FOOD_PER_PERSON = 1


# ---------------------------------------------------------------- 创建 / 恢复

def _defaults():
    return copy.deepcopy(_DEFAULTS)


def new_game():
    """创建新对局:食物、队列与各类台账全部清空。"""
    return _defaults()


def _normalize(state):
    """损坏状态恢复:补齐缺失字段、纠正类型、修复不变量。"""
    if not isinstance(state, dict):
        return _defaults()
    for key, default in _DEFAULTS.items():
        state.setdefault(key, copy.deepcopy(default))
    for key in _LIST_FIELDS:
        if not isinstance(state[key], list):
            state[key] = []
    if not isinstance(state["events"], dict):
        state["events"] = {}
    else:
        # 读档后 JSON 对象键是字符串,恢复为整数编号;无法恢复的条目丢弃
        rebuilt = {}
        for key, value in state["events"].items():
            try:
                rebuilt[int(key)] = value
            except (TypeError, ValueError):
                continue
        state["events"] = rebuilt
    for key in _INT_FIELDS:
        value = state[key]
        if isinstance(value, bool) or not isinstance(value, int):
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = _DEFAULTS[key]
            state[key] = value
    state["closed"] = bool(state["closed"])
    # 不变量:编号连续不跳号、账目与占用不为负、占用不超过容量
    state["next_id"] = max(1, state["next_id"])
    if state["events"]:
        state["next_id"] = max(state["next_id"], max(state["events"]) + 1)
    state["src"] = max(0, state["src"])
    state["dst"] = max(0, state["dst"])
    state["cap"] = max(0, state["cap"])
    state["used"] = min(max(0, state["used"]), state["cap"])
    state["settled"] = max(0, state["settled"])
    state["clock"] = max(0, state["clock"])
    return state


# ---------------------------------------------------------------- 存档 / 读档

def dump_game(state):
    """存档:序列化规范化后的状态。"""
    return json.dumps(_normalize(state), ensure_ascii=False, sort_keys=True)


def load_game(data):
    """读档:整体替换为存档内容(不残留当前食物),并修复损坏数据。

    存档损坏或不是合法 JSON 时恢复为初始状态。
    """
    try:
        raw = json.loads(data)
    except (TypeError, ValueError):
        raw = None
    state = _defaults()
    if isinstance(raw, dict):
        for key in _DEFAULTS:
            if key in raw:
                state[key] = raw[key]
    return _normalize(state)


# ---------------------------------------------------------------- 推进原语

def _snapshot(state):
    return copy.deepcopy(state)


def _restore(state, snapshot):
    state.clear()
    state.update(snapshot)


def _touch(state):
    """推进操作生效后,重置 / 整备重新可用。"""
    if _RESET_TOKEN in state["processed"]:
        state["processed"].remove(_RESET_TOKEN)


def _mark_done(state, token):
    """幂等台账:同一对象重复处理时第二次起失败。"""
    if token in state["processed"]:
        return False
    state["processed"].append(token)
    return True


def _alloc_id(state):
    """分配编号:先取当前值再自增,连续不跳号。"""
    rid = state["next_id"]
    state["next_id"] = rid + 1
    return rid


def _can_admit(state):
    """统一收容守卫:未锁定、队列非空、隔离间未满。"""
    return (
        not state["closed"]
        and bool(state["queue"])
        and state["used"] < state["cap"]
    )


# ---------------------------------------------------------------- 业务操作

def bug_0(state):
    """处理当前队首难民;同一难民重复处理时第二次起失败。"""
    state = _normalize(state)
    head = state["queue"][0] if state["queue"] else None
    return _mark_done(state, "refugee:%r" % (head,))


def bug_3(state):
    """查看队首难民(只查看不移除);空队列返回空值。"""
    state = _normalize(state)
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_6(state):
    """盘点食物数量。"""
    state = _normalize(state)
    return len(state["items"])


def bug_9(state):
    """分配下一个编号(读档后同样连续,不跳号)。"""
    state = _normalize(state)
    return _alloc_id(state)


def bug_12(state):
    """结算在住人员伙食(幂等事务)。

    单次收容只结算一次差额;库存不足时完整回滚,不留下重复累计。
    """
    state = _normalize(state)
    due = state["used"] * _FOOD_PER_PERSON - state["settled"]
    if due <= 0:
        return True
    snapshot = _snapshot(state)
    state["src"] -= due
    if state["src"] < 0:
        _restore(state, snapshot)
        return False
    state["dst"] += due
    state["settled"] += due
    _touch(state)
    return True


def bug_15(state):
    """收容前置检查:暂停 / 锁定、空队列或满员时禁止收容。"""
    state = _normalize(state)
    return _can_admit(state)


def bug_18(state):
    """重置 / 整备:清空食物与在途状态;已整备时重复调用失败。"""
    state = _normalize(state)
    if _RESET_TOKEN in state["processed"]:
        return False
    state["queue"] = []
    state["items"] = []
    state["src"] = _DEFAULTS["src"]
    state["dst"] = _DEFAULTS["dst"]
    state["used"] = 0
    state["settled"] = 0
    state["processed"] = [_RESET_TOKEN]
    return True


def bug_21(state):
    """从隔离间放行一人;空隔离间返回空值(None)而非占位文本。"""
    state = _normalize(state)
    if state["used"] <= 0:
        return None
    state["used"] -= 1
    _touch(state)
    return True


def bug_24(state):
    """调度下一个事件:先到达的先处理;无事件返回空值。"""
    state = _normalize(state)
    if not state["events"]:
        return None
    return min(state["events"].items(), key=lambda item: item[1][0])[0]


def bug_27(state):
    """收容队首难民进入隔离间(先到先得)。

    暂停 / 锁定、空队列或隔离间满员时失败且不改动状态。
    """
    state = _normalize(state)
    if not _can_admit(state):
        return False
    refugee = state["queue"].pop(0)
    rid = _alloc_id(state)
    state["used"] += 1
    state["events"][rid] = (state["clock"], refugee)
    state["clock"] += 1
    _touch(state)
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
