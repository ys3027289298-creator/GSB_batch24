"""高山气象站 —— 状态机视图
==============================

状态（state["status"]）:
    "paused"   待机/暂停：禁止上报，可查看任务、恢复运行
    "running"  运行中：可接收观测任务、上报观测数据
    "locked"   已锁定：观测窗达到上限或余额不足时进入，需重置解锁

转移:
    new_game()        -> "paused"          开机自检，默认待机
    resume(state)     "paused"  -> "running"
    pause(state)      "running" -> "paused"
    上报时观测窗满    "running" -> "locked"（自动锁定）
    bug_8(state)      任意      -> "paused"  重置：清空电力与观测窗

不变量（check_invariants，暂停/恢复/序列化/读档/重开后都必须成立）:
    1. status 属于 {"paused", "running", "locked"}
    2. 0 <= used <= cap，且 balance >= 0、count >= 0
    3. edges 的两端节点必须都存在于 nodes（不留悬空边）
    4. next_id 严格大于 events/queue 中已出现的任务编号（读档后不跳号）
    5. 失败操作整体回滚：任何校验不通过时状态保持原样，不留半份修改

序列化:
    serialize/load 使用 JSON，顶层键名不变；
    edges 的元组键、nodes/events 的整数键在读档时还原，next_id 随档保存。
"""

import json

STATUS_PAUSED = "paused"
STATUS_RUNNING = "running"
STATUS_LOCKED = "locked"

REPORT_COST = 20


def new_game():
    return {
        'nodes': {1: True, 2: True},
        'edges': {(1, 2): 5},
        'queue': [],
        'count': 0,
        'balance': 10,
        'accounts': {},
        'events': {1: True},
        'used': 1,
        'cap': 2,
        'status': STATUS_PAUSED,
        'next_id': 2,
    }


def check_invariants(state):
    """校验状态机不变量，违反时抛出 ValueError。"""
    if state["status"] not in (STATUS_PAUSED, STATUS_RUNNING, STATUS_LOCKED):
        raise ValueError("非法状态: %r" % state["status"])
    if not 0 <= state["used"] <= state["cap"]:
        raise ValueError("观测窗用量越界: used=%r cap=%r" % (state["used"], state["cap"]))
    if state["balance"] < 0 or state["count"] < 0:
        raise ValueError("电力或余额为负")
    for edge in state["edges"]:
        for node in edge:
            if node not in state["nodes"]:
                raise ValueError("悬空边: %r" % (edge,))
    seen = list(state["events"]) + list(state["queue"])
    if seen and state["next_id"] <= max(seen):
        raise ValueError("读档后编号跳号: next_id=%r" % state["next_id"])
    return True


def pause(state):
    """运行中 -> 暂停；其余状态为无操作。"""
    if state["status"] == STATUS_RUNNING:
        state["status"] = STATUS_PAUSED
    return state["status"]


def resume(state):
    """暂停 -> 运行中；锁定状态必须先重置，不能直接恢复。"""
    if state["status"] == STATUS_PAUSED:
        state["status"] = STATUS_RUNNING
    return state["status"]


def serialize(state):
    """把同一份状态序列化为 JSON 文本（顶层键名不变）。"""
    check_invariants(state)
    data = dict(state)
    data["nodes"] = {str(key): value for key, value in state["nodes"].items()}
    data["edges"] = {"%d,%d" % edge: weight for edge, weight in state["edges"].items()}
    data["events"] = {str(key): value for key, value in state["events"].items()}
    return json.dumps(data, ensure_ascii=False)


def load(payload):
    """读档：还原键类型与 next_id（不跳号），并重新校验不变量。"""
    data = json.loads(payload)
    data["nodes"] = {int(key): value for key, value in data["nodes"].items()}
    data["edges"] = {
        tuple(int(part) for part in key.split(",")): weight
        for key, weight in data["edges"].items()
    }
    data["events"] = {int(key): value for key, value in data["events"].items()}
    check_invariants(data)
    return data


def bug_2(state):
    """从观测窗取出最早进入的任务；空窗返回 None，不再返回占位文本。"""
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def bug_5(state):
    """查看队首观测任务：只读不删，先来先看。"""
    if not state["queue"]:
        return None
    return state["queue"][0]


def bug_8(state):
    """重置/读档后清空电力：count 与观测窗用量归零，回到暂停态。"""
    state["count"] = 0
    state["used"] = 0
    state["status"] = STATUS_PAUSED
    return True


def bug_11(state):
    """上报观测数据：余额不足或观测窗满时整体失败，不留半份修改。

    成功时恰好扣一次费用、累计一次电力，不会重复累计。
    """
    if state["status"] != STATUS_RUNNING:
        return False
    if state["used"] >= state["cap"]:
        state["status"] = STATUS_LOCKED
        return False
    if state["balance"] < REPORT_COST:
        return False
    state["balance"] -= REPORT_COST
    state["used"] += 1
    state["count"] += 1
    return True


def bug_14(state):
    """查询账户电力：不存在的账户按 0 计，不少算一。"""
    return state["accounts"].get("missing", 0)


def bug_17(state):
    """暂停或锁定状态下禁止上报，直接失败。"""
    if state["status"] != STATUS_RUNNING:
        return False
    if state["used"] >= state["cap"]:
        return False
    state["used"] += 1
    return True


def bug_20(state):
    """处理最早进入的观测任务（FIFO），处理后将其移出事件表。"""
    if not state["events"]:
        return None
    oldest = next(iter(state["events"]))
    del state["events"][oldest]
    return oldest


def bug_23(state):
    """剩余观测窗容量：cap - used，不少算一。"""
    return state["cap"] - state["used"]


def bug_26(state):
    """处理观测任务 1：同一任务重复处理时第二次直接失败。"""
    task_id = 1
    if task_id in state["events"]:
        return False
    state["events"][task_id] = True
    return True


def bug_29(state):
    """移除节点 1：级联删除关联边，保持无悬空边不变量。"""
    state["nodes"].pop(1, None)
    state["edges"] = {
        edge: weight for edge, weight in state["edges"].items() if 1 not in edge
    }
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
