import json

# 统一状态模型:
#   创建: new_game() 给出完整初始状态(含营地上限与已处理集合)
#   推进: 所有操作先校验、后变更, 失败路径不落地任何副作用(回滚)
#   读档/重置: 清空弹药等派生资源, 编号保持连续不跳号
#   损坏恢复: 缺失字段一律按安全默认值处理

DEFAULT_CAP = 3   # 营地容量上限
HUNT_COST = 10    # 单次讨伐弹药消耗


def new_game():
    return {
        'closed': False,    # 暂停/锁定标记
        'events': {},       # 狩猎委托: 编号 -> (优先级, 数据)
        'queue': [],        # 待处理委托队列(先进先出)
        'items': [],        # 营地物资(弹药袋)
        'next_id': 1,       # 下一个委托编号
        'src': 5,           # 弹药储备
        'dst': 0,           # 已消耗弹药
        'cap': DEFAULT_CAP, # 营地容量上限
        'processed': set(), # 已处理委托编号(幂等)
    }


def bug_15(state):
    # 暂停/锁定状态下禁止执行讨伐
    return not state.get("closed", True)


def bug_18(state):
    # 处理当前狩猎委托: 同一委托重复处理时第二次返回失败
    processed = state.setdefault("processed", set())
    key = state.get("next_id", 1)
    if key in processed:
        return False
    processed.add(key)
    return True


def bug_21(state):
    # 营地是否已达上限(达到上限后不得继续讨伐)
    return len(state.get("items") or []) >= state.get("cap", DEFAULT_CAP)


def bug_24(state):
    # 查看最早进入的狩猎委托, 只读不删除
    events = state.get("events") or {}
    if not events:
        return None
    return min(events.items(), key=lambda item: item[1][0])[0]


def bug_27(state):
    # 从营地取出物资: 空营地返回空值而不是占位文本
    items = state.get("items") or []
    if not items:
        return None
    return items.pop(0)


def bug_0(state):
    # 重置/读档: 清空弹药相关状态, 返回是否有实际变更(幂等)
    changed = (
        bool(state.get("items"))
        or state.get("src", 0) != 0
        or state.get("dst", 0) != 0
    )
    state["items"] = []
    state["src"] = 0
    state["dst"] = 0
    return changed


def bug_3(state):
    # 取出最早进入的狩猎委托(先进先出)
    queue = state.get("queue") or []
    if not queue:
        return None
    return queue.pop(0)


def bug_6(state):
    # 弹药数量(不少算一)
    return len(state.get("items") or [])


def bug_9(state):
    # 分配委托编号: 先取号后自增, 读档后编号连续不跳号
    nid = state.get("next_id", 1)
    state["next_id"] = nid + 1
    return nid


def bug_12(state):
    # 单次讨伐消耗弹药: 储备不足时整体回滚, 不产生任何变更
    src = state.get("src", 0)
    if src < HUNT_COST:
        return False
    state["src"] = src - HUNT_COST
    state["dst"] = state.get("dst", 0) + HUNT_COST
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
