import unittest

import core


class TestCore(unittest.TestCase):
    def test_00(self):
        state = core.new_game()
        state.update({'audit': [('a', 1), ('b', 2)]})
        rows = core.bug_16(state)
        self.assertTrue(all(row[0] == "a" for row in rows))

    def test_01(self):
        state = core.new_game()
        state.update({'slots': 0, 'cap': 2})
        state["slots"] = 2
        self.assertFalse(core.bug_19(state))

    def test_02(self):
        state = core.new_game()
        self.assertTrue(core.bug_22(state))

    def test_03(self):
        state = core.new_game()
        state.update({'paused': False, 'clock': 0})
        state["paused"] = True
        self.assertEqual(core.bug_25(state), 0)

    def test_04(self):
        state = core.new_game()
        self.assertFalse(core.bug_28(state))

    def test_05(self):
        state = core.new_game()
        state.update({'items': [], 'cap': 2})
        state["items"] = ["a", "b"]
        self.assertFalse(core.bug_1(state))

    def test_06(self):
        state = core.new_game()
        state.update({'paused': False})
        state["paused"] = True
        self.assertFalse(core.bug_4(state))

    def test_07(self):
        state = core.new_game()
        state.update({'count': 0})
        self.assertEqual(core.bug_7(state), 1)

    def test_08(self):
        state = core.new_game()
        state.update({'amount': 0})
        self.assertFalse(core.bug_10(state))

    def test_09(self):
        state = core.new_game()
        state.update({'src': 10, 'dst': 0})
        core.bug_13(state)
        self.assertEqual(state["dst"], 5)


if __name__ == "__main__":
    unittest.main()
