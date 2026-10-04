import json

# 状态不变量（幽灵船调查）:
# src/dst   : 灵异值资源；任何消耗必须先校验余额，不足则整体失败且零副作用
# closed    : 暂停/锁定；为真时禁止一切记录
# events    : 已记录线索，键为编号，值首列(seq)为进入顺序；先进入的先处理 (FIFO)
# queue     : 待处理线索队列，队首为最早进入；“查看”只读不移除
# items/cap : 船舱已存线索与容量；空船舱返回 None；达到容量禁止再记录
#             (cap 由设置/读档提供，缺省视为 0，即未知容量一律拒绝记录)
# next_id   : 下一个可分配编号；只进不退、不跳号，且不与已有编号冲突
# 去重标记持久化在 state 内（重复操作幂等，且 JSON 读档后仍然有效）


def new_game():
    return {'src': 5, 'dst': 0, 'closed': False, 'events': {}, 'queue': [], 'items': [], 'next_id': 1}

def bug_12(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    return True

def bug_15(state):
    if state.get("closed"):
        return False
    return True

def bug_18(state):
    if state.get("haunt_counted"):
        return False
    state["haunt_counted"] = True
    return True

def bug_21(state):
    if not state["items"]:
        return None
    return state["items"][0]

def bug_24(state):
    events = state["events"]
    if not events:
        return None
    return min(events, key=lambda key: events[key][0])

def bug_27(state):
    return len(state["items"]) < state.get("cap", 0)

def bug_0(state):
    if state.get("clue_done"):
        return False
    state["clue_done"] = True
    return True

def bug_3(state):
    queue = state["queue"]
    if not queue:
        return None
    return queue[0]

def bug_6(state):
    return len(state["items"])

def bug_9(state):
    used = [int(key) for key in state.get("events", {})]
    next_id = max(state.get("next_id", 1), max(used, default=0) + 1)
    state["next_id"] = next_id + 1
    return next_id

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
