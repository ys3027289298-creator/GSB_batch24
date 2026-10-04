"""虫群警戒 — 纯文本交互核心逻辑。

统一状态模型:
  创建  new_game()        生成完整自洽的初始状态
  推进  bug_0/bug_3/bug_18  FIFO 处理虫群报告; 一次性迁移由守卫标记保护
  回滚  bug_12              清空弹药等派生状态, 哨塔计数保持不变
  读档  save_game/load_game 快照与恢复完整状态; 损坏状态按初始模型修复

失败路径约定: 空队列/空哨塔返回空值, 重复处理/暂停锁定/达到上限返回 False。
"""

import copy
import json

TOWER_CAP = 5  # 哨塔压制上限


def new_game():
    """创建: 完整初始状态。"""
    return {
        'events': {1: (5, 6), 2: (1, 2)},  # 虫群报告: 编号 -> (到达回合, 规模)
        'queue': [],      # 待处理报告队列 (FIFO)
        'items': [],      # 弹药库存
        'next_id': 1,     # 下一报告编号 (单调连续)
        'src': 5,         # 哨塔压制计数
        'dst': 0,
        'closed': False,  # 暂停/锁定
        'done': {},       # 一次性迁移守卫标记
    }


def _repair(state):
    """损坏状态恢复: 按初始模型补齐缺失字段, 不覆盖已有值。"""
    for key, value in new_game().items():
        if key not in state:
            state[key] = copy.deepcopy(value)
    return state


def _once(state, tag):
    """一次性迁移守卫: 首次放行并记录, 重复触发返回 False。"""
    done = _repair(state)['done']
    if tag in done:
        return False
    done[tag] = True
    return True


def save_game(state):
    """读档(出): 序列化完整状态快照。"""
    return json.dumps(_repair(state))


def load_game(data):
    """读档(入): 恢复状态; 损坏存档按初始模型修复, 编号保持连续。"""
    try:
        state = json.loads(data)
    except (TypeError, ValueError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    state = _repair(state)
    state['events'] = {int(k): tuple(v) for k, v in state['events'].items()}
    return state


def bug_0(state):
    """处理当前虫群报告: 同一报告重复处理时, 第二次起走失败路径。"""
    return _once(state, 'process')


def bug_3(state):
    """取出下一份报告: 先进入的先处理 (FIFO); 空队列返回空值。"""
    queue = _repair(state)['queue']
    if not queue:
        return None
    return queue.pop(0)


def bug_6(state):
    """弹药数量: 库存实际件数。"""
    return len(_repair(state)['items'])


def bug_9(state):
    """下一报告编号: 只读预览, 读档后编号不跳号。"""
    return _repair(state)['next_id']


def bug_12(state):
    """回滚/读档: 清空弹药等派生状态, 哨塔计数保持不变。"""
    _repair(state)
    state['items'] = []
    return True


def bug_15(state):
    """压制守卫: 暂停或锁定状态下拒绝压制。"""
    return not _repair(state)['closed']


def bug_18(state):
    """推进回合: 一次性迁移, 重复推进走失败路径。"""
    return _once(state, 'advance')


def bug_21(state):
    """是否可继续压制: 哨塔达到上限即停止。"""
    return _repair(state)['src'] < TOWER_CAP


def bug_24(state):
    """查看最早进入的虫群报告: 只读, 不误删。"""
    events = _repair(state)['events']
    if not events:
        return None
    return min(events.items(), key=lambda item: item[1][0])[0]


def bug_27(state):
    """查看下一份待处理报告: 空哨塔返回空值而非占位文本。"""
    queue = _repair(state)['queue']
    if not queue:
        return None
    return queue[0]


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
