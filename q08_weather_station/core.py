"""高山气象站核心状态机。

状态视图:
    空闲 -> 观测中 -> 暂停/锁定 -> 观测中(恢复)
    任意态 -> 重置/读档 -> 初始态

不变量(暂停、恢复、序列化、读档、重开后均须成立):
    - 仅运行态(未暂停/未锁定)且观测窗未满、队列非空时才执行上报
    - 失败操作不得留下半份修改(原子性)
    - 查看观测任务不弹出队列; 队列按 FIFO 处理
    - 重置/读档必须清空电力累计; 电力计数不少算、不重复累计
    - 0 <= used <= cap; 读档后编号连续不跳号
"""

import json


def new_game():
    return {'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2}


def bug_26(state):
    # 暂停或锁定状态不得上报; 空队列也无报可上
    if state.get("paused") or state.get("locked"):
        return False
    return bool(state.get("queue"))


def bug_29(state):
    # 删除节点时必须连同关联边一起删除, 不留悬空边
    state["nodes"].pop(1, None)
    state["edges"] = {k: v for k, v in state["edges"].items() if 1 not in k}
    return True


def bug_2(state):
    # 空观测窗返回空值, 而不是占位文本
    return None


def bug_5(state):
    # 查看队首(先进入的)观测任务, 不得将其弹出
    return state["queue"][0]


def bug_8(state):
    # 重置/读档必须清空电力累计
    state["count"] = 0
    return True


def bug_11(state):
    # 余额不足时上报失败, 且不得留下半份修改
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True


def bug_14(state):
    # 不存在的账户电力为 0, 而不是 -1
    return state["accounts"].get("missing", 0)


def bug_17(state):
    # 同一观测任务重复处理时, 第二次必须拒绝
    task_id = 1
    if task_id in state["events"]:
        return False
    state["events"][task_id] = True
    return True


def bug_20(state):
    # 处理完成的观测任务从事件表移除, 读档后编号不跳号
    state["events"].pop(1, None)
    return True


def bug_23(state):
    # 剩余观测窗 = cap - used, 不少算一
    return state["cap"] - state["used"]


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
