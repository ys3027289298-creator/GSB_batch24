import json

import core


def snapshot(state):
    return json.loads(json.dumps(state, default=list))


def check(name, cond):
    if not cond:
        raise AssertionError(name)
    print("PASS", name)


def expect_rollback(name, state, fn):
    before = snapshot(state)
    result = fn(state)
    check(name, result is False and snapshot(state) == before)


REPLAY_OPS = [
    ("tick", core.bug_25),
    ("transfer", core.bug_13),
    ("count", core.bug_7),
    ("recycle", core.bug_1),
    ("slot", core.bug_19),
]


def replay(initial):
    state = snapshot(initial)
    results = []
    for name, fn in REPLAY_OPS:
        results.append((name, fn(state)))
    return results, state


def main():
    state = core.new_game()
    state["paused"] = True
    before = snapshot(state)
    check("paused does not advance", core.bug_25(state) == 0 and snapshot(state) == before)

    expect_rollback("full workshop rejected",
                    {**core.new_game(), "items": ["a", "b"]}, core.bug_1)
    expect_rollback("full slots rejected",
                    {**core.new_game(), "slots": 2}, core.bug_19)
    expect_rollback("insufficient energy rejected", core.new_game(), core.bug_10)

    state = core.new_game()
    before = snapshot(state)
    check("empty workshop returns empty value", core.bug_28(state) is None and snapshot(state) == before)

    state = core.new_game()
    rows = core.bug_16(state)
    check("fifo peek is non destructive",
          len(state["audit"]) == 2 and all(row[0] == "a" for row in rows))

    state = core.new_game()
    core.bug_13(state)
    check("energy conserved", state["src"] == 5 and state["dst"] == 5)
    check("energy counted exactly once", core.bug_7(core.new_game()) == 1)

    state = {**core.new_game(), "amount": 9, "dst": 9}
    clock_before = state["clock"]
    check("reset succeeds", core.bug_22(state) is True)
    check("reset clears energy", state["amount"] == 0 and state["dst"] == 0)
    check("reset keeps numbering continuous", state["clock"] == clock_before)

    origin = core.new_game()
    origin["clock"] = 4
    saved = json.dumps(origin, default=list)
    results1, final1 = replay(origin)
    results2, final2 = replay(json.loads(saved))
    check("save load replay identical",
          results1 == results2 and final1 == final2)
    check("no id skip after load", final2["clock"] == final1["clock"])

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
