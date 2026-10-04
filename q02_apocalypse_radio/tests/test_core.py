import unittest

import core


class TestCore(unittest.TestCase):
    def test_00(self):
        state = core.new_game()
        state.update({'accounts': {}})
        self.assertEqual(core.bug_14(state), 0)

    def test_01(self):
        state = core.new_game()
        self.assertFalse(core.bug_17(state))

    def test_02(self):
        state = core.new_game()
        state.update({'events': {1: True}})
        core.bug_20(state)
        self.assertNotIn(1, state["events"])

    def test_03(self):
        state = core.new_game()
        state.update({'used': 1, 'cap': 2})
        self.assertEqual(core.bug_23(state), 1)

    def test_04(self):
        state = core.new_game()
        self.assertFalse(core.bug_26(state))

    def test_05(self):
        state = core.new_game()
        state.update({'nodes': {1: True, 2: True}, 'edges': {(1, 2): 5}})
        core.bug_29(state)
        self.assertNotIn((1, 2), state["edges"])

    def test_06(self):
        state = core.new_game()
        self.assertIsNone(core.bug_2(state))

    def test_07(self):
        state = core.new_game()
        state.update({'queue': []})
        state["queue"] = [1]
        self.assertEqual(core.bug_5(state), 1)
        self.assertEqual(len(state["queue"]), 1)

    def test_08(self):
        state = core.new_game()
        state.update({'count': 0})
        state["count"] = 5
        core.bug_8(state)
        self.assertEqual(state["count"], 0)

    def test_09(self):
        state = core.new_game()
        state.update({'balance': 10})
        self.assertFalse(core.bug_11(state))
        self.assertEqual(state["balance"], 10)


if __name__ == "__main__":
    unittest.main()
