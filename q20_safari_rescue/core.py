"""野生动物救援 —— 状态机视图与不变量

状态（new_game 返回的同一份 dict，JSON 键名固定）：
  events   待处理事件/动物集合 {id: True}
  used/cap 保护区已用容量 / 上限（不变量：0 <= used <= cap）
  nodes    保护区节点集合；edges 节点间转移边 {(a, b): 代价}
  queue    待救援队列（FIFO：先进先出）
  count    麻醉剂计数（重置/读档后必须清零）
  balance  资金（不变量：>= 0，扣费失败不得留下半份修改）
  accounts 麻醉剂台账（缺失条目视为 0）

状态机：
  ACTIVE --pause--> PAUSED --resume--> ACTIVE
  任意态 --serialize--> JSON --load--> 同构状态（编号连续、count 清零）
  任意态 --reset--> new_game() 初始态

转移规则：
  处理事件：事件存在则移除并成功；重复处理同一动物必须失败。
  转移动物：暂停/锁定、容量满（used >= cap）、资金不足时整体失败，
            不得修改任何字段；成功才一次性扣费并占用容量。
  查看队列：只读，不得误删队首动物。
  删除节点：连同关联边一起删除，不留悬挂边。
"""

import json


def new_game():
    return {'events': {1: True}, 'used': 1, 'cap': 2, 'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}, 'queue': [], 'count': 0, 'balance': 10, 'accounts': {}}

def bug_20(state):
    # 处理动物：同一动物只能成功处理一次，第二次必须失败
    if 1 in state["events"]:
        del state["events"][1]
        return True
    return False

def bug_23(state):
    # 剩余容量 = 上限 - 已用；达到上限（返回 0）后禁止继续转移
    return state["cap"] - state["used"]

def bug_26(state):
    # 暂停或锁定状态下禁止执行转移
    return bool(state.get("paused") or state.get("locked"))

def bug_29(state):
    # 删除节点时连同关联边一起删除，不留悬挂边
    state["nodes"].pop(1, None)
    state["edges"] = {edge: cost for edge, cost in state["edges"].items()
                      if 1 not in edge}
    return True

def bug_2(state):
    # 空保护区返回空值，而不是占位文本
    if not state["queue"]:
        return None
    return state["queue"][0]

def bug_5(state):
    # 查看队首动物：只读，不得误删
    if not state["queue"]:
        return None
    return state["queue"][0]

def bug_8(state):
    # 重置/读档：麻醉剂计数必须清零
    state["count"] = 0
    return True

def bug_11(state):
    # 单次转移只扣一次麻醉剂费用；资金不足整体失败，不留半份修改
    cost = 20
    if state["balance"] < cost:
        return False
    state["balance"] -= cost
    return True

def bug_14(state):
    # 缺失的麻醉剂台账条目按 0 计，不少算
    return state["accounts"].get("missing", 0)

def bug_17(state):
    # 读档后编号必须连续（1..n），出现跳号则拒绝
    ids = sorted(state["events"])
    return ids != list(range(1, len(ids) + 1))

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
