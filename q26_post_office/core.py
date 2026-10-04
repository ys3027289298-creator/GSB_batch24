"""星际邮局 —— 状态机视图

状态（state dict，JSON 键名固定）：
  queue    分拣线队列（FIFO，先进先出）
  count    已处理包裹计数
  balance  邮局信用点余额
  accounts 各账户信用点
  events   活动事件/状态标记；事件 1 = 锁定（暂停）标记
  used     分拣线已用槽位
  cap      分拣线容量上限
  nodes    投递网络节点
  edges    投递网络边 {(src, dst): 费用}

不变量（暂停、恢复、序列化、读档、重开后均须成立）：
  I1  0 <= used <= cap
  I2  锁定期间（1 in events）禁止投递
  I3  分拣线为空时取件返回 None，不伪造成功、不返回占位文本
  I4  失败操作不得留下半份修改（先校验，后变更）
  I5  edges 不得引用已删除的节点
  I6  序列化/读档后编号连续、信用点以存档为准；重置清空信用点
"""

import json


def new_game():
    return {'queue': [], 'count': 0, 'balance': 10, 'accounts': {}, 'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}}


def invariants_hold(state):
    """校验状态机不变量 I1/I5。"""
    if not (0 <= state["used"] <= state["cap"]):
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
    """读档：整体替换状态（不残留读档前的信用点），边键还原为元组，编号不跳号。"""
    data = json.loads(payload)
    data["events"] = {int(key): value for key, value in data["events"].items()}
    data["nodes"] = {int(key): value for key, value in data["nodes"].items()}
    data["edges"] = {tuple(int(part) for part in key.split(",")): cost for key, cost in data["edges"].items()}
    return data


def bug_2(state):
    """处理分拣线下一件包裹：空线返回 None（I3）；FIFO 先进入先处理。"""
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def bug_5(state):
    """查看队首包裹：只读不移除；空线返回 None。"""
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_8(state):
    """重置：清空计数与信用点等运行态（I6），保留容量与网络拓扑。"""
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
    """投递守卫：锁定（事件 1）或分拣线达到上限时禁止投递（I1/I2）。"""
    if 1 in state["events"]:
        return False
    if state["used"] >= state["cap"]:
        return False
    return True


def bug_20(state):
    """结算后清除已处理事件，避免单次投递重复累计信用点。"""
    state["events"].pop(1, None)
    return True


def bug_23(state):
    """分拣线剩余槽位：cap - used，不少算一。"""
    return state["cap"] - state["used"]


def bug_26(state):
    """分拣线是否已满：达到上限即拒收（I1）。"""
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
