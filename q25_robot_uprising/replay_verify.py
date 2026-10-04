"""可重复的快照回滚与重放验证（纯标准库）。

用法: python replay_verify.py
验证三类不变量:
  1. 失败不变更: 任何返回 False/None 的操作，状态与操作前快照完全一致。
  2. 快照回滚:   失败后回滚到快照，再重放成功操作序列，结果与无故障路径一致。
  3. 持久化往返: save_state/load_state 往返后状态等价，重置清空能源与编号。
"""
import copy
import json

import core

OPS = [
    ('advance', core.bug_25),
    ('inspect', core.bug_28),
    ('admit', core.bug_1),
    ('process', core.bug_4),
    ('recycle', core.bug_7),
    ('spend', core.bug_10),
    ('transfer', core.bug_13),
    ('view', core.bug_16),
    ('slot_check', core.bug_19),
    ('reset', core.bug_22),
]


def snapshot(state):
    return copy.deepcopy(state)


def check_failure_atomicity():
    """对每个操作构造失败场景，断言失败后状态逐键不变。"""
    failures = 0
    scenarios = {
        'advance': lambda s: s.update(paused=True),
        'inspect': lambda s: (s.update(paused=True), s.update(items=[])),
        'admit': lambda s: (s.update(items=['a', 'b']), s.update(slots=2)),
        'process': lambda s: s.update(paused=True),
        'spend': lambda s: s.update(amount=0),
        'transfer': lambda s: s.update(src=0),
        'slot_check': lambda s: s.update(slots=2),
    }
    for name, op in OPS:
        if name not in scenarios:
            continue
        state = core.new_game()
        scenarios[name](state)
        before = snapshot(state)
        result = op(state)
        assert result in (False, None), (name, result)
        assert state == before, (name, state, before)
        failures += 1
    return failures


def check_rollback_replay():
    """注入失败 -> 回滚到快照 -> 重放同一操作序列，与无故障基线一致。"""
    script = [
        ('admit', core.bug_1),
        ('admit', core.bug_1),   # 重复单位，幂等拒绝
        ('advance', core.bug_25),
        ('transfer', core.bug_13),
        ('inspect', core.bug_28),
        ('advance', core.bug_25),
    ]
    baseline = core.new_game()
    for _, op in script:
        op(baseline)

    snap = core.new_game()
    faulty = snapshot(snap)
    faulty['paused'] = True  # 故障注入：暂停态下所有操作必须失败且不变更
    for _, op in script:
        op(faulty)
    assert faulty['paused'] is True
    assert faulty['clock'] == 0 and faulty['items'] == [], faulty

    rolled_back = snapshot(snap)  # 回滚到故障前快照
    for _, op in script:          # 重放
        op(rolled_back)
    assert rolled_back == baseline, (rolled_back, baseline)
    return len(script)


def check_persistence_roundtrip():
    """JSON 往返等价；重置/读档清空能源(amount/dst)与编号(count/clock)。"""
    state = core.new_game()
    core.bug_1(state)
    core.bug_13(state)
    core.bug_7(state)
    core.bug_25(state)
    blob = core.save_state(state)
    restored = core.load_state(blob)
    assert restored == state, (restored, state)
    assert json.loads(blob)['amount'] == state['amount']

    core.bug_22(restored)  # 重置：能源与编号清零
    assert restored['amount'] == 0 and restored['dst'] == 0
    assert restored['count'] == 0 and restored['clock'] == 0
    assert restored['items'] == [] and restored['slots'] == 0
    return 1


def check_fifo_and_energy():
    """FIFO 顺序与能源单次累计。"""
    state = core.new_game()
    state['items'] = ['u1', 'u2']
    state['slots'] = 2
    assert core.bug_28(state) == 'u1'   # 先进入的先处理
    assert core.bug_28(state) == 'u2'
    assert core.bug_28(state) is None   # 空车间返回空值
    assert state['slots'] == 0

    energy = core.new_game()
    assert core.bug_13(energy) is True
    assert (energy['src'], energy['dst']) == (5, 5)  # 单次回收只累计一次
    energy['amount'] = 5
    assert core.bug_10(energy) is True
    assert energy['amount'] == 0
    energy2 = core.new_game()
    energy2['amount'] = 0
    assert core.bug_10(energy2) is False  # 能源不足不扣成负数
    assert energy2['amount'] == 0
    return 1


def main():
    checks = [
        ('failure_atomicity', check_failure_atomicity),
        ('rollback_replay', check_rollback_replay),
        ('persistence_roundtrip', check_persistence_roundtrip),
        ('fifo_and_energy', check_fifo_and_energy),
    ]
    for name, fn in checks:
        n = fn()
        print(f'PASS {name} ({n} assertions groups)')
    print('ALL REPLAY CHECKS PASSED')


if __name__ == '__main__':
    main()
