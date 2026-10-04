import json

PIT_CAPACITY = 2
WATER_SUPPLY = 5
REGISTER_COST = 1


def new_game():
    return {'events': {1: (5, 6), 2: (1, 2)}, 'queue': [], 'items': [], 'next_id': 1, 'src': 5, 'dst': 0, 'closed': False}


def _invariants_ok(state):
    """State invariants restored before any fix:

    - next_id is always greater than every registered event id (no id reuse/skips)
    - src + dst is conserved by transfers; both stay non-negative
    - events never exceed the pit capacity
    - closed is a boolean gate for all mutating operations
    """
    events = state.get("events", {})
    if events and state.get("next_id", 1) <= max(events):
        return False
    if state.get("src", 0) < 0 or state.get("dst", 0) < 0:
        return False
    if len(events) > PIT_CAPACITY:
        return False
    return True


def _normalize(state):
    """Re-establish invariants after load/reset: water counters are
    rebalanced and next_id is recomputed from the registered events."""
    events = {int(key): value for key, value in state.setdefault("events", {}).items()}
    state["events"] = events
    state["next_id"] = (max(events) + 1) if events else 1
    state["src"] = WATER_SUPPLY
    state["dst"] = 0
    return state


def bug_24(state):
    """查看文物：返回最新登记的文物编号，只读，绝不删除。"""
    events = state["events"]
    if not events:
        return None
    return max(events)


def bug_27(state):
    """发掘坑容量检查：达到上限后不允许继续登记。"""
    return len(state["events"]) < PIT_CAPACITY


def bug_0(state):
    """处理当前文物：一次操作消耗整份水源（src -> dst）并只成功一次；
    暂停/锁定时拒绝；重复处理同一文物第二次返回失败（水源已耗尽）。"""
    if state["closed"]:
        return False
    if state["src"] < WATER_SUPPLY:
        return False
    state["src"] -= WATER_SUPPLY
    state["dst"] += WATER_SUPPLY
    return True


def bug_3(state):
    """按先来后到取出队首文物（FIFO）。"""
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def bug_6(state):
    """水源统计：返回当前已清点的文物/水量总数。"""
    return len(state["items"])


def bug_9(state):
    """读取下一个可用编号（预览/读档恢复）：只读不分配，不跳号。"""
    events = state.get("events", {})
    if events and state["next_id"] <= max(events):
        state["next_id"] = max(events) + 1
    return state["next_id"]


def bug_12(state):
    """登记一件文物：先校验全部前置条件，任一不满足则整体回滚，
    不产生任何副作用；成功时只扣一次水。"""
    if state["closed"]:
        return False
    if not state["queue"]:
        return False
    if len(state["events"]) >= PIT_CAPACITY:
        return False
    if state["src"] < REGISTER_COST:
        return False
    item = state["queue"].pop(0)
    event_id = state["next_id"]
    state["events"][event_id] = (item, 0)
    state["items"].append(item)
    state["next_id"] = event_id + 1
    state["src"] -= REGISTER_COST
    state["dst"] += REGISTER_COST
    return True


def bug_15(state):
    """登记闸门：暂停或锁定状态下拒绝登记。"""
    return not state["closed"]


def bug_18(state):
    """重置：清空水源与全部进度；已处于初始状态时重复重置返回失败。"""
    clean = (
        not state["events"]
        and not state["queue"]
        and not state["items"]
        and state["src"] == 0
        and state["dst"] == 0
        and state["next_id"] == 1
        and not state["closed"]
    )
    if clean:
        return False
    state["events"] = {}
    state["queue"] = []
    state["items"] = []
    state["next_id"] = 1
    state["src"] = 0
    state["dst"] = 0
    state["closed"] = False
    state.pop("_processed", None)
    return True


def bug_21(state):
    """查看队首文物：空发掘坑返回空值，只读不移除。"""
    if not state["queue"]:
        return None
    return state["queue"][0]


def save_game(state, path):
    _normalize(state)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def load_game(path):
    with open(path, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    return _normalize(state)


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
