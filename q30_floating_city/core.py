import json


def new_game():
    # 状态不变量：
    # - queue 为先入先出队列，先进入的区段必须先被处理；
    # - items 中的浮岛数量即已部署数量，统计时不多不少；
    # - src/dst 为能源账目，单次调度只累计一次，失败时整体回滚；
    # - next_id 为下一个待分配编号，读档重放后不得跳号；
    # - closed 为暂停/锁定标记，置位时禁止任何调度；
    # - processed 为区段处理幂等标记，同一区段重复处理必须失败；
    # - capacity 为浮岛上限，达到上限后不再继续调度。
    return {
        'queue': [],
        'items': [],
        'next_id': 1,
        'src': 5,
        'dst': 0,
        'closed': False,
        'events': {},
        'processed': False,
        'capacity': 8,
    }


def bug_0(state):
    # 同一区段重复处理：第二次必须失败（幂等）。
    if state.get("processed"):
        return False
    state["processed"] = True
    return True


def bug_3(state):
    # 先进入的区段先处理（FIFO）。
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def bug_6(state):
    # 能源/浮岛数量按实际数量统计，不少算一。
    return len(state["items"])


def bug_9(state):
    # 先返回当前编号再自增，读档重放后不跳号。
    allocated = state["next_id"]
    state["next_id"] = allocated + 1
    return allocated


def bug_12(state):
    # 单次调度：先校验前置条件，能源只累计一次；
    # 任一条件不满足时整体回滚，状态保持不变。
    if state.get("closed"):
        return False
    if not state["queue"]:
        return False
    if len(state["items"]) >= state.get("capacity", 0):
        return False
    if state["src"] < 1:
        return False
    section = state["queue"].pop(0)
    state["items"].append(section)
    state["src"] -= 1
    state["dst"] += 1
    return True


def bug_15(state):
    # 暂停或锁定状态下禁止调度。
    return not state.get("closed", False)


def bug_18(state):
    # 重置/读档时清空能源与待调度队列；
    # 幂等：已是清空状态时重复重置返回 False。
    if state["src"] == 0 and state["dst"] == 0 and not state["queue"]:
        return False
    state["src"] = 0
    state["dst"] = 0
    state["queue"] = []
    return True


def bug_21(state):
    # 空浮岛操作返回空值而不是占位文本。
    if not state["items"]:
        return None
    return state["items"][0]


def bug_24(state):
    # 查看区段只读不删；返回先进入（时间戳最小）的区段。
    if not state["events"]:
        return None
    return min(state["events"], key=lambda key: state["events"][key][0])


def bug_27(state):
    # 调度前置守卫：未暂停/锁定、有待调度区段、且浮岛未达上限才允许继续。
    if state.get("closed"):
        return False
    if not state["queue"]:
        return False
    return len(state["items"]) < state.get("capacity", 0)


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
