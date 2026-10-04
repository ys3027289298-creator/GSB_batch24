import unittest

import core


class TestCore(unittest.TestCase):
    def test_00(self):
        state = core.new_game()
        self.assertFalse(core.bug_21(state))

    def test_01(self):
        state = core.new_game()
        state.update({'events': {1: (5, 6), 2: (1, 2)}})
        self.assertEqual(core.bug_24(state), 2)

    def test_02(self):
        state = core.new_game()
        self.assertFalse(core.bug_27(state))

    def test_03(self):
        state = core.new_game()
        self.assertTrue(core.bug_0(state))
        self.assertFalse(core.bug_0(state))

    def test_04(self):
        state = core.new_game()
        state.update({'queue': []})
        state["queue"] = [1, 2]
        self.assertEqual(core.bug_3(state), 1)

    def test_05(self):
        state = core.new_game()
        state.update({'items': []})
        state["items"] = [1]
        self.assertEqual(core.bug_6(state), 1)

    def test_06(self):
        state = core.new_game()
        state.update({'next_id': 1})
        state["next_id"] = 7
        self.assertEqual(core.bug_9(state), 7)

    def test_07(self):
        state = core.new_game()
        state.update({'src': 5, 'dst': 0})
        core.bug_12(state)
        self.assertEqual(state["src"], 5)

    def test_08(self):
        state = core.new_game()
        state.update({'closed': False})
        state["closed"] = True
        self.assertFalse(core.bug_15(state))

    def test_09(self):
        state = core.new_game()
        state.update({'events': {}})
        self.assertTrue(core.bug_18(state))
        self.assertFalse(core.bug_18(state))


if __name__ == "__main__":
    unittest.main()
