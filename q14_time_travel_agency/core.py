"""时间旅行局 —— 状态机视图

状态（state 字典的 JSON 键名保持不变）：
    count    时间币计数（重置/读档后必须清零）
    balance  时间币余额（派遣扣费前必须校验，失败不得留下半份修改）
    accounts 账户表（查询不存在的账户返回 0，而不是占位值）
    events   已登记行程（处理完成的行程必须移除；重复处理返回失败）
    used/cap 时间门已用/上限（剩余额度 = cap - used，达到上限禁止派遣）
    nodes    时间门节点（删除节点必须级联删除关联边）
    edges    节点间连线
    queue    待处理行程队列（先进先出；查看只读不删除）

状态机：
    READY  --派遣(余额充足 且 used<cap 且未暂停/锁定)--> READY (used+1, 扣费, 计币一次)
    READY  --暂停/锁定--> PAUSED/LOCKED（禁止派遣）
    PAUSED --恢复--> READY
    任意态 --重置/读档--> READY (count 清零, 编号连续不跳号)

不变量：
    - 失败操作返回 False/None，且不修改任何状态。
    - 同一行程不可重复处理；单次派遣只累计一次时间币。
    - 查看行程是只读操作；空时间门操作返回空值 None。
"""

import json


def new_game():
    return {'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': []}

def bug_8(state):
    # 重置/读档：清空时间币计数
    state["count"] = 0
    return True

def bug_11(state):
    # 派遣扣费：余额不足则整体失败，不留下半份修改
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def bug_14(state):
    # 查询账户时间币：不存在的账户为 0，不少算一
    return state["accounts"].get("missing", 0)

def bug_17(state):
    # 处理行程：同一行程重复处理时返回失败
    if 1 in state["events"]:
        return False
    state["events"][1] = True
    return True

def bug_20(state):
    # 完成行程：处理后将行程从登记表移除
    state["events"].pop(1, None)
    return True

def bug_23(state):
    # 时间门剩余额度：cap - used，达到上限（返回 0）即禁止派遣
    return state["cap"] - state["used"]

def bug_26(state):
    # 暂停或锁定状态下禁止派遣：返回是否被阻止
    return bool(state.get("paused")) or state["used"] >= state["cap"]

def bug_29(state):
    # 删除时间门节点：级联删除与之相连的边
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        state["edges"].pop(edge, None)
    return True

def bug_2(state):
    # 空时间门操作：返回空值而不是占位文本
    return None

def bug_5(state):
    # 查看队首行程：只读，不从队列中删除
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
