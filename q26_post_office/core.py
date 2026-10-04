"""星际邮局 —— 状态机视图

状态（state dict，JSON 键名固定不变）：
  queue    分拣线队列（FIFO：先进入的包裹先处理）
  count    已处理包裹计数，兼作包裹编号基数（读档须原样恢复，编号不跳号）
  balance  邮局信用点余额
  accounts 各账户信用点
  events   事件台账；事件 1 = 暂停/锁定标记，兼作投递结算幂等标记
  used     分拣线已用槽位
  cap      分拣线容量上限
  nodes    投递网络节点
  edges    投递网络边 {(src, dst): 费用}

状态机：
  运行 --暂停--> 锁定（events 含 1） --恢复/结算--> 运行（events 移除 1）
  锁定期间禁止投递；分拣线达到上限（used >= cap）即拒收，不再继续投递。

不变量（暂停、恢复、序列化、读档、重开后均须成立）：
  I1  0 <= used <= cap
  I2  锁定期间（1 in events）不得执行投递
  I3  空分拣线取件/查看返回 None（空值），不返回占位文本
  I4  失败操作零副作用：先校验，后变更，不留半份修改
  I5  edges 不得引用已删除的节点
  I6  重置与读档清空信用点（以存档/初始为准）；读档恢复 count，编号连续
  I7  投递结算幂等：同一包裹重复结算仍返回成功，信用点不重复累计
"""

import json


def new_game():
    return {'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}}


def invariants_hold(state):
    """校验状态机不变量 I1/I5 及非负计数。"""
    if not (0 <= state["used"] <= state["cap"]):
        return False
    if state["count"] < 0 or state["balance"] < 0:
        return False
    if any(a not in state["nodes"] or b not in state["nodes"] for a, b in state["edges"]):
        return False
    return True


def save_game(state):
    """序列化为 JSON 文本；边键 (a, b) 编码为 "a,b"，保证读档可还原。"""
    payload = dict(state)
    payload["edges"] = {"%d,%d" % edge: cost for edge, cost in state["edges"].items()}
    return json.dumps(payload)


def load_game(payload):
    """读档：整体替换状态（不残留读档前的信用点），键型还原，编号不跳号。

    count 原样恢复，后续包裹编号连续；读档结果必须满足不变量。
    """
    data = json.loads(payload)
    data["events"] = {int(key): value for key, value in data["events"].items()}
    data["nodes"] = {int(key): value for key, value in data["nodes"].items()}
    data["edges"] = {tuple(int(part) for part in key.split(",")): cost for key, cost in data["edges"].items()}
    if not invariants_hold(data):
        raise ValueError("存档违反状态机不变量")
    return data


def bug_2(state):
    """处理分拣线下一件包裹。

    修复：空分拣线返回 None（空值）而非占位文本（I3）；
    FIFO 队首出队，先进入的包裹先处理。
    """
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def bug_5(state):
    """查看队首包裹（只读）。

    修复：查看不再误删包裹；空分拣线返回 None。
    """
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_8(state):
    """重置邮局运行态。

    修复：重置清空信用点（balance/accounts）及计数、队列、事件、
    已用槽位（I6），保留容量与网络拓扑。
    """
    state["queue"] = []
    state["count"] = 0
    state["balance"] = 0
    state["accounts"] = {}
    state["events"] = {}
    state["used"] = 0
    return True


def bug_11(state):
    """扣费投递：余额不足则失败且零副作用（I4），成功才扣 20。"""
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True


def bug_14(state):
    """查询账户信用点：未知账户为 0，不少算一。"""
    return state["accounts"].get("missing", 0)


def bug_17(state):
    """投递守卫：暂停/锁定（事件 1）或分拣线达到上限时禁止投递（I1/I2）。"""
    if 1 in state["events"]:
        return False
    if state["used"] >= state["cap"]:
        return False
    return True


def bug_20(state):
    """投递结算：清除已处理事件，信用点不重复累计。

    幂等（I7）：同一包裹重复结算仍返回 True（成功），不产生二次累计。
    """
    state["events"].pop(1, None)
    return True


def bug_23(state):
    """分拣线剩余槽位：cap - used，不少算一。"""
    return state["cap"] - state["used"]


def bug_26(state):
    """分拣线是否已满：达到上限即拒收，不再继续投递（I1）。"""
    return state["used"] >= state["cap"]


def bug_29(state):
    """移除节点并清理其关联边，不留悬挂边（I5）。"""
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        del state["edges"][edge]
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
