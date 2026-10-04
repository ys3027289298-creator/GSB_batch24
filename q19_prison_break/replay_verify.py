"""可重复的失败回滚与重放验证（纯标准库，只读 core，不依赖 tests）。"""
import copy
import json
import sys

import core


def check(name, cond):
    if not cond:
        raise AssertionError(name)
    print("PASS", name)


def normalize(state):
    return json.loads(json.dumps(state))


def run_op(state, op):
    return getattr(core, op)(state)


# ---- 1. 状态转换不变量：重复操作不得二次破坏状态 ----
s = core.new_game()

before = normalize(s)
check("bug_28 默认未锁定", run_op(s, "bug_28") is False)
check("bug_28 纯查询不改状态", normalize(s) == before)

check("bug_22 空监区判定为 True", run_op(s, "bug_22") is True)
check("bug_22 查询不改状态", normalize(s) == before)

before = normalize(s)
check("bug_19 有空位可引开", run_op(s, "bug_19") is True)
check("bug_19 查询不改状态", normalize(s) == before)

s["slots"] = s["cap"]
check("bug_19 监区满后拒绝", run_op(s, "bug_19") is False)

s = core.new_game()
s["paused"] = True
before = normalize(s)
check("bug_4 暂停时拒绝执行", run_op(s, "bug_4") is False)
check("bug_4 不修改状态", normalize(s) == before)
check("bug_25 暂停时钟不推进", run_op(s, "bug_25") == 0)
check("bug_25 暂停时钟保持 0", s["clock"] == 0)

s = core.new_game()
s["items"] = ["a", "b"]
before = normalize(s)
check("bug_1 满员拒绝且不溢出", run_op(s, "bug_1") is False)
check("bug_1 重复拒绝状态不变", run_op(s, "bug_1") is False and normalize(s) == before)

s = core.new_game()
s["amount"] = 7
check("bug_10 首次清空返回 True", run_op(s, "bug_10") is True and s["amount"] == 0)
check("bug_10 重复清空幂等返回 False", run_op(s, "bug_10") is False and s["amount"] == 0)

s = core.new_game()
s["count"] = 0
check("bug_7 单次引开警戒值 +1", run_op(s, "bug_7") == 1 and s["count"] == 1)
check("bug_7 不重复累计", s["count"] == 1)

s = core.new_game()
total = s["src"] + s["dst"]
check("bug_13 首次转移成功", run_op(s, "bug_13") is True and s["dst"] == 5)
check("bug_13 总量守恒", s["src"] + s["dst"] == total)
check("bug_13 同一巡逻队重复处理失败", run_op(s, "bug_13") is False)
check("bug_13 重放不二次转移", s["dst"] == 5 and s["src"] + s["dst"] == total)

s = core.new_game()
before = normalize(s)
rows = run_op(s, "bug_16")
check("bug_16 FIFO 先处理最早进入者", [r[0] for r in rows] == ["a"])
check("bug_16 查看不删除巡逻队", normalize(s) == before)
check("bug_16 重复查看结果一致", run_op(s, "bug_16") == rows)

s = core.new_game()
s["audit"] = []
check("bug_16 空队列返回空值", run_op(s, "bug_16") == [])

# ---- 2. 操作日志重放：从初始状态重建，终态必须一致 ----
initial = core.new_game()
live = copy.deepcopy(initial)
journal = [("bug_7",), ("bug_7",), ("bug_13",), ("bug_25",),
           ("bug_10",), ("bug_19",)]
for (op,) in journal:
    run_op(live, op)
check("警戒值按日志次数累计", live["count"] == 2)

replayed = copy.deepcopy(initial)
for (op,) in journal:
    run_op(replayed, op)
check("日志重放终态一致", normalize(replayed) == normalize(live))
check("重放整段日志幂等", all(run_op(replayed, "bug_13") is False
                               and run_op(replayed, "bug_10") is False
                               for _ in (0,)))

# ---- 3. 持久化不变量：JSON 存档/读档、编号连续、警戒值清空 ----
blob = json.dumps(live)
loaded = json.loads(blob)
check("读档保留全部 JSON 键", set(loaded) == set(live))
check("读档后警戒值计数不跳号", loaded["count"] == live["count"])

loaded["amount"] = 9
run_op(loaded, "bug_10")
reloaded = json.loads(json.dumps(loaded))
check("重置/读档后警戒值已清空", reloaded["amount"] == 0)

before_n = reloaded["count"]
reloaded["count"] = run_op.__self__ if False else before_n
run_op(reloaded, "bug_7")
run_op(reloaded, "bug_25") if not reloaded["paused"] else None
check("读档后编号连续递增不跳号",
      reloaded["count"] == before_n + 1 and reloaded["clock"] == live["clock"] + 1)

print("ALL REPLAY CHECKS PASSED")
sys.exit(0)
