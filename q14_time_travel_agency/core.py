"""时间旅行局核心状态机。

状态机视图
----------
状态: READY(营业中) / PAUSED(暂停) / LOCKED(锁定)
  - PAUSED 或 LOCKED 下禁止派遣; 恢复(READY)后才可派遣。
资源: count(时间币) / balance(账户余额) / used/cap(时间门占用/上限)
  - 不变量: 0 <= used <= cap, count >= 0。
  - 扣费原子: 余额不足则整体失败, 不留半份修改。
  - 重置/读档/重开后 count 必须清零。
行程: queue(待处理行程, FIFO) / events(已登记行程, 按进入顺序处理)
  - 查看不删除; 空时间门返回 None; 同一行程不可重复处理。
图: nodes/edges 一致, 删除节点须级联删除关联边。
序列化/读档/重开后上述不变量必须仍然成立。
"""

import json


def new_game():
    return {'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': []}


def bug_8(state):
    # 重置/读档: 清空时间币, 保证重开后不变量成立
    state["count"] = 0
    return True


def bug_11(state):
    # 派遣扣费: 余额不足则整体失败, 不留下半份修改
    cost = 20
    if state["balance"] < cost:
        return False
    state["balance"] -= cost
    return True


def bug_14(state):
    # 查询缺失账户: 返回 0, 编号不跳号
    return state["accounts"].get("missing", 0)


def bug_17(state):
    # 暂停或锁定状态下禁止派遣; 时间门达到上限后不再派遣
    if state.get("status", "paused") != "ready":
        return False
    if state["used"] >= state["cap"]:
        return False
    state["used"] += 1
    return True


def bug_20(state):
    # 处理行程: 先进入的先处理(FIFO)
    if not state["events"]:
        return False
    first = next(iter(state["events"]))
    del state["events"][first]
    return True


def bug_23(state):
    # 剩余时间门容量: 不少算一
    return state["cap"] - state["used"]


def bug_26(state):
    # 处理队首行程: 同一行程不可重复处理, 空队列失败
    if not state["queue"]:
        return False
    state["queue"].pop(0)
    return True


def bug_29(state):
    # 删除节点: 级联删除关联边, 不留半份修改
    state["nodes"].pop(1, None)
    state["edges"] = {edge: w for edge, w in state["edges"].items() if 1 not in edge}
    return True


def bug_2(state):
    # 空时间门: 返回空值 None, 而非占位文本
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_5(state):
    # 查看队首行程: 只看不删
    if not state["queue"]:
        return None
    return state["queue"][0]


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
