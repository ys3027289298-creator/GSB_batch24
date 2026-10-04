import json


# 统一状态模型使用的常量。
DEFAULT_SRC = 5          # 初始/重置/读档后水源地的水量
WATER_PER_ALLOCATION = 10  # 单次分配的水量（只扣减、累计各一次）
CAMP_CAPACITY = 1        # 营地可容纳的补给数量


def new_game():
    """创建（重置）状态：编号从 1 开始、水源清空、无挂起补给。"""
    return {
        'queue': [],        # 待处理补给编号，先进先出
        'items': [],        # 已分配到营地的补给编号
        'next_id': 1,       # 下一个补给编号（先取号、后自增）
        'src': DEFAULT_SRC, # 水源地剩余水量
        'dst': 0,           # 营地累计水量
        'closed': False,    # 暂停/锁定标记
        'events': {},       # 分配日志：事件号 -> (分配前 src, 分配前 dst)，供回滚
    }


def _is_processed(state, supply):
    return supply in state["items"]


def _camp_full(state):
    return len(state["items"]) >= CAMP_CAPACITY


def bug_0(state):
    """推进：处理当前补给。

    同一补给重复处理时，第二次起返回 False，不重复登记。
    """
    supply = state["next_id"]
    if _is_processed(state, supply):
        return False
    state["items"].append(supply)
    return True


def bug_3(state):
    """推进：取出最先进入队列的补给（先进先出）；空队列返回 None。"""
    queue = state.get("queue")
    if not isinstance(queue, list) or not queue:
        return None
    return queue.pop(0)


def bug_6(state):
    """查询营地补给数量，如实计数（不少算一）。"""
    items = state.get("items")
    return len(items) if isinstance(items, list) else 0


def bug_9(state):
    """创建：分配补给编号。先返回当前编号再自增，读档后不跳号。"""
    supply = state["next_id"]
    state["next_id"] = supply + 1
    return supply


def bug_12(state):
    """推进：单次水源分配。

    水量充足时 src 扣减一次、dst 累计一次并记录事件；
    水量不足或处于暂停/锁定状态时失败，状态保持不变。
    """
    if state["closed"] or state["src"] < WATER_PER_ALLOCATION:
        return False
    event_id = max(state["events"], default=0) + 1
    state["events"][event_id] = (state["src"], state["dst"])
    state["src"] -= WATER_PER_ALLOCATION
    state["dst"] += WATER_PER_ALLOCATION
    return True


def bug_15(state):
    """推进前置检查：暂停或锁定状态下拒绝执行分配。"""
    return not state.get("closed", False)


def bug_18(state):
    """推进：把补给分配到营地。

    营地达到容量上限（或暂停/锁定）时拒绝分配，否则取一个补给入营。
    """
    if state["closed"] or _camp_full(state):
        return False
    if state["queue"]:
        supply = state["queue"].pop(0)
    else:
        supply = bug_9(state)
    state["items"].append(supply)
    return True


def bug_21(state):
    """查询：只查看下一个待处理补给，不将其移除。

    队列为空（空营地）时返回 None，而不是占位文本。
    """
    queue = state.get("queue")
    if not isinstance(queue, list) or not queue:
        return None
    return queue[0]


def bug_24(state):
    """回滚：撤销最近一次分配并恢复分配前的水量，返回事件号。

    没有可回滚的事件时返回 None；损坏的事件记录仅移除，不污染状态。
    """
    events = state.get("events")
    if not isinstance(events, dict) or not events:
        return None
    event_id = max(events)
    snapshot = events.pop(event_id)
    try:
        src_before, dst_before = snapshot
    except (TypeError, ValueError):
        return event_id
    state["src"] = src_before
    state["dst"] = dst_before
    return event_id


def bug_27(state, snapshot=None):
    """读档：从 JSON 快照（字符串或字典）恢复统一状态。

    读档后水源清空（src 复位、dst 归零），编号严格沿用快照、不跳号；
    快照缺失或损坏时回退到初始状态并返回 False，成功恢复返回 True。
    """
    if snapshot is None:
        return False
    try:
        data = json.loads(snapshot) if isinstance(snapshot, str) else dict(snapshot)
    except (TypeError, ValueError):
        data = None
    if not isinstance(data, dict):
        state.update(new_game())
        return False

    queue = data.get("queue", [])
    items = data.get("items", [])
    raw_events = data.get("events", {})
    if not isinstance(queue, list) or not isinstance(items, list) or not isinstance(raw_events, dict):
        state.update(new_game())
        return False

    events = {}
    for key, value in raw_events.items():
        try:
            events[int(key)] = tuple(value)
        except (TypeError, ValueError):
            state.update(new_game())
            return False

    restored = new_game()
    restored["queue"] = queue
    restored["items"] = items
    restored["events"] = events
    restored["closed"] = bool(data.get("closed", False))
    # 水源在读档时清空，不沿用快照里的累计值。

    supply_ids = set(restored["queue"]) | set(restored["items"])
    max_known = max(supply_ids, default=0)
    saved_next_id = data.get("next_id")
    if isinstance(saved_next_id, int) and saved_next_id > max_known:
        restored["next_id"] = saved_next_id
    else:
        restored["next_id"] = max_known + 1

    state.update(restored)
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
