"""避难所防守：统一的创建 / 推进 / 回滚 / 读档状态模型。

状态字段（由 new_game 创建，_ensure 负责损坏状态恢复）：
  queue      等待区难民编号队列（先进先出）
  quarantine 隔离间（容量 QUARANTINE_CAPACITY）
  processed  已处理过的难民编号（同一难民不可重复处理）
  items      食物库存（每份食物一个条目）
  next_id    下一个可分配的难民编号
  src / dst  仓库 / 避难所物资
  closed     暂停或锁定标记
  events     事件表 {事件编号: (时间, 内容)}
  history    快照栈（回滚用，不随存档序列化）
"""

import copy
import json

QUARANTINE_CAPACITY = 1
TRANSFER_AMOUNT = 10


def new_game():
    return {
        "queue": [],
        "quarantine": [],
        "processed": [],
        "items": [],
        "next_id": 1,
        "src": 5,
        "dst": 0,
        "closed": False,
        "events": {},
        "history": [],
    }


# ---------------------------------------------------------------- 状态模型

def _ensure(state):
    """损坏状态恢复：补全缺失字段并纠正非法取值。"""
    if not isinstance(state, dict):
        raise TypeError("state must be a dict")
    for key, value in new_game().items():
        if key not in state or not isinstance(state[key], type(value)):
            state[key] = value
    if state["next_id"] < 1:
        state["next_id"] = 1
    if state["src"] < 0:
        state["src"] = 0
    if state["dst"] < 0:
        state["dst"] = 0
    return state


def reset_game(state):
    """重置：恢复初始状态并清空食物等全部进度，保留快照栈。"""
    history = state.get("history") if isinstance(state, dict) else None
    state.clear()
    state.update(new_game())
    state["history"] = history if isinstance(history, list) else []
    return state


def snapshot(state):
    """推进前留档：把当前状态的深拷贝压入快照栈。"""
    _ensure(state)
    state["history"].append(
        copy.deepcopy({key: value for key, value in state.items() if key != "history"})
    )
    return state


def rollback(state):
    """回滚到最近一次快照；没有可回滚快照时返回 False。"""
    _ensure(state)
    if not state["history"]:
        return False
    snap = state["history"].pop()
    history = state["history"]
    state.clear()
    state.update(copy.deepcopy(snap))
    state["history"] = history
    return True


def save_game(state):
    """存档：把状态序列化为 JSON（不含快照栈）。"""
    _ensure(state)
    return json.dumps({key: value for key, value in state.items() if key != "history"})


def load_game(state, raw):
    """读档：恢复存档，清空食物并修复编号；损坏存档返回 False。"""
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    history = state.get("history") if isinstance(state.get("history"), list) else []
    state.clear()
    state.update(data)
    _ensure(state)
    state["items"] = []
    state["next_id"] = _repaired_next_id(state)
    state["history"] = history
    return True


def _repaired_next_id(state):
    """读档后编号不跳号也不冲突：接续存档值，且避开所有在册编号。"""
    known = list(state["queue"]) + list(state["quarantine"]) + list(state["processed"])
    used = [rid for rid in known if isinstance(rid, int) and not isinstance(rid, bool)]
    nxt = state["next_id"]
    if not isinstance(nxt, int) or isinstance(nxt, bool):
        nxt = 1
    return max([1, nxt] + [rid + 1 for rid in used])


# ---------------------------------------------------------------- 推进操作

def _alloc_id(state):
    """分配编号：先取号后自增，保证不跳号。"""
    _ensure(state)
    rid = state["next_id"]
    state["next_id"] = rid + 1
    return rid


def _can_admit(state):
    """暂停或锁定状态下禁止收容。"""
    _ensure(state)
    return not state["closed"]


def _admit(state):
    """收容新难民进隔离间：锁定或满员时失败，且不落任何副作用。"""
    _ensure(state)
    if state["closed"] or len(state["quarantine"]) >= QUARANTINE_CAPACITY:
        return False
    state["quarantine"].append(_alloc_id(state))
    return True


def _next_waiting(state):
    """按到达顺序取下一个等待难民；空队列返回 None。"""
    _ensure(state)
    if not state["queue"]:
        return None
    return state["queue"].pop(0)


def _food_count(state):
    _ensure(state)
    return len(state["items"])


def _transfer(state, amount):
    """物资调拨：数量非法或库存不足时失败，且双方都不变。"""
    _ensure(state)
    if amount <= 0 or state["src"] < amount:
        return False
    state["src"] -= amount
    state["dst"] += amount
    return True


def _process(state, rid):
    """处理难民：同一编号只允许成功处理一次。"""
    _ensure(state)
    if rid in state["processed"]:
        return False
    state["processed"].append(rid)
    return True


def _release(state):
    """放出隔离间最早进入的难民；空隔离间返回 None。"""
    _ensure(state)
    if not state["quarantine"]:
        return None
    return state["quarantine"].pop(0)


def _peek_event(state):
    """查看时间最早的事件编号，不删除；无事件返回 None。"""
    _ensure(state)
    if not state["events"]:
        return None
    return min(state["events"].items(), key=lambda item: item[1][0])[0]


def _intake(state):
    """完整收容：等待区队首进入隔离间，并只登记一份食物。

    任一前置条件不满足时整体失败，不产生任何副作用。
    """
    _ensure(state)
    if state["closed"] or not state["queue"]:
        return False
    if len(state["quarantine"]) >= QUARANTINE_CAPACITY:
        return False
    rid = state["queue"].pop(0)
    state["quarantine"].append(rid)
    state["items"].append("ration")
    return True


# ---------------------------------------------------------------- 交互入口

def bug_0(state):
    return _admit(state)


def bug_3(state):
    return _next_waiting(state)


def bug_6(state):
    return _food_count(state)


def bug_9(state):
    return _alloc_id(state)


def bug_12(state):
    return _transfer(state, TRANSFER_AMOUNT)


def bug_15(state):
    return _can_admit(state)


def bug_18(state):
    _ensure(state)
    return _process(state, state["next_id"])


def bug_21(state):
    return _release(state)


def bug_24(state):
    return _peek_event(state)


def bug_27(state):
    return _intake(state)


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
