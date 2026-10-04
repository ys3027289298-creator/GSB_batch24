import copy
import json

import core

OPS = [
    ("can_schedule_full_slot", lambda s: core.bug_19(s)),
    ("airlock_empty_result", lambda s: core.bug_22(s)),
    ("advance_paused_clock", lambda s: core.bug_25(s)),
    ("duplicate_request", lambda s: core.bug_28(s)),
    ("enqueue_request", lambda s: core.bug_1(s)),
    ("dispatch_when_paused", lambda s: core.bug_4(s)),
    ("add_oxygen", lambda s: core.bug_7(s)),
    ("spend_supplies", lambda s: core.bug_10(s)),
    ("transfer_air", lambda s: core.bug_13(s)),
    ("view_audit_readonly", lambda s: core.bug_16(s)),
]


def snapshot(state):
    return json.dumps(state, sort_keys=True)


def restore(blob):
    return json.loads(blob)


def run_ops(state, times):
    log = []
    for _ in range(times):
        for name, op in OPS:
            log.append((name, op(state)))
    return state, log


def main():
    failures = 0

    base = core.new_game()
    blob0 = snapshot(base)

    # 1) 重放：同一快照重放两次操作序列，最终状态必须逐字节一致
    run1, log1 = run_ops(restore(blob0), 1)
    run2, log2 = run_ops(restore(blob0), 1)
    if snapshot(run1) != snapshot(run2) or log1 != log2:
        failures += 1
        print("FAIL replay determinism")
    else:
        print("ok   replay determinism")

    # 2) 幂等守卫：重复请求/暂停/上限/只读查看均不得改变状态
    guards_ok = True

    s = core.new_game()
    core.bug_1(s)
    snap = snapshot(s)
    if core.bug_1(s) is not False or snapshot(s) != snap:
        guards_ok = False  # 同一补给请求重复处理

    s = core.new_game()
    s["paused"] = True
    snap = snapshot(s)
    if core.bug_25(s) != 0 or core.bug_4(s) is not False or snapshot(s) != snap:
        guards_ok = False  # 暂停状态仍推进/调度

    s = core.new_game()
    s["slots"] = s["cap"]
    s["items"] = ["x"] * s["cap"]
    snap = snapshot(s)
    if core.bug_19(s) is not False or core.bug_1(s) is not False or snapshot(s) != snap:
        guards_ok = False  # 达到上限仍继续调度/入队

    s = core.new_game()
    snap = snapshot(s)
    if core.bug_10(s) is not False or snapshot(s) != snap:
        guards_ok = False  # 数量不足仍扣减

    s = core.new_game()
    s["src"] = 3
    snap = snapshot(s)
    if core.bug_13(s) is not False or snapshot(s) != snap:
        guards_ok = False  # 源不足仍转移

    s = core.new_game()
    snap = snapshot(s)
    core.bug_16(s)
    if snapshot(s) != snap:
        guards_ok = False  # 查看补给请求时误删

    s = core.new_game()
    if core.bug_28(s) is not False:
        guards_ok = False  # 重复处理第二次仍成功

    if guards_ok:
        print("ok   idempotency guards")
    else:
        failures += 1
        print("FAIL idempotency guards")

    # 3) 失败回滚：制造非法操作后回滚到快照，状态必须完全恢复
    roll = restore(blob0)
    core.bug_1(roll)
    core.bug_7(roll)
    core.bug_13(roll)
    if snapshot(roll) == blob0:
        failures += 1
        print("FAIL mutation did not happen")
    rolled_back = restore(snapshot(roll))  # checkpoint
    core.bug_1(rolled_back)
    core.bug_13(rolled_back)
    rolled_back = restore(snapshot(roll))  # rollback to checkpoint
    if snapshot(rolled_back) != snapshot(roll):
        failures += 1
        print("FAIL rollback")
    else:
        print("ok   rollback")

    # 4) 读档不变量：回滚到初始快照后再重放，结果与 run1 一致
    again, _ = run_ops(restore(blob0), 1)
    if snapshot(again) != snapshot(run2):
        failures += 1
        print("FAIL load-and-replay")
    else:
        print("ok   load-and-replay")

    print("RESULT", "ALL PASS" if failures == 0 else f"{failures} FAILED")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
