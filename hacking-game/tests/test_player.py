"""Tests for engine/player.py — Player state management."""

import unittest
from engine.player import Player


class TestPlayerInit(unittest.TestCase):
    def setUp(self):
        self.p = Player('Ghost')

    def test_defaults(self):
        self.assertEqual(self.p.name, 'Ghost')
        self.assertEqual(self.p.level, 1)
        self.assertEqual(self.p.credits, 0)
        self.assertEqual(self.p.trace_exposure, 0)
        self.assertEqual(self.p.tools, [])
        self.assertAlmostEqual(self.p.trace_multiplier, 1.0)

    def test_repr(self):
        self.assertIn('Ghost', repr(self.p))


class TestToolManagement(unittest.TestCase):
    def setUp(self):
        self.p = Player('Ghost')

    def test_add_tool(self):
        result = self.p.add_tool('port_scanner')
        self.assertTrue(result)
        self.assertIn('port_scanner', self.p.tools)

    def test_add_duplicate_tool(self):
        self.p.add_tool('port_scanner')
        result = self.p.add_tool('port_scanner')
        self.assertFalse(result)
        self.assertEqual(self.p.tools.count('port_scanner'), 1)

    def test_has_tool_true(self):
        self.p.add_tool('vpn_shield')
        self.assertTrue(self.p.has_tool('vpn_shield'))

    def test_has_tool_false(self):
        self.assertFalse(self.p.has_tool('vpn_shield'))

    def test_use_tool_removes_it(self):
        self.p.add_tool('root_kit')
        result = self.p.use_tool('root_kit')
        self.assertTrue(result)
        self.assertNotIn('root_kit', self.p.tools)

    def test_use_tool_not_owned(self):
        result = self.p.use_tool('root_kit')
        self.assertFalse(result)


class TestTraceMechanics(unittest.TestCase):
    def setUp(self):
        self.p = Player('Ghost')

    def test_increase_trace(self):
        caught = self.p.increase_trace(20)
        self.assertEqual(self.p.trace_exposure, 20)
        self.assertFalse(caught)

    def test_is_caught_at_max(self):
        self.p.increase_trace(100)
        self.assertTrue(self.p.is_caught())

    def test_trace_capped_at_100(self):
        self.p.increase_trace(200)
        self.assertEqual(self.p.trace_exposure, Player.MAX_TRACE)

    def test_reset_trace(self):
        self.p.increase_trace(50)
        self.p.reset_trace()
        self.assertEqual(self.p.trace_exposure, 0)

    def test_trace_multiplier_halved(self):
        self.p.trace_multiplier = 0.5
        self.p.increase_trace(20)
        self.assertEqual(self.p.trace_exposure, 10)

    def test_trace_multiplier_minimum_1(self):
        """Even a tiny amount of trace must add at least 1."""
        self.p.trace_multiplier = 0.001
        self.p.increase_trace(1)
        self.assertEqual(self.p.trace_exposure, 1)

    def test_increase_trace_returns_true_when_caught(self):
        caught = self.p.increase_trace(100)
        self.assertTrue(caught)


class TestProgression(unittest.TestCase):
    def setUp(self):
        self.p = Player('Ghost')

    def test_level_up(self):
        result = self.p.level_up()
        self.assertTrue(result)
        self.assertEqual(self.p.level, 2)

    def test_level_up_at_max(self):
        self.p.level = Player.MAX_LEVEL
        result = self.p.level_up()
        self.assertFalse(result)
        self.assertEqual(self.p.level, Player.MAX_LEVEL)


class TestSerialisation(unittest.TestCase):
    def test_round_trip(self):
        p = Player('Spectre')
        p.level = 3
        p.credits = 2500
        p.trace_exposure = 40
        p.add_tool('vpn_shield')

        data = p.to_dict()
        restored = Player.from_dict(data)

        self.assertEqual(restored.name, 'Spectre')
        self.assertEqual(restored.level, 3)
        self.assertEqual(restored.credits, 2500)
        self.assertEqual(restored.trace_exposure, 40)
        self.assertIn('vpn_shield', restored.tools)

    def test_from_dict_missing_keys_use_defaults(self):
        p = Player.from_dict({'name': 'Anon'})
        self.assertEqual(p.level, 1)
        self.assertEqual(p.credits, 0)
        self.assertEqual(p.trace_exposure, 0)
        self.assertEqual(p.tools, [])

    def test_to_dict_does_not_include_multiplier(self):
        """trace_multiplier is runtime state — not persisted."""
        data = Player('Ghost').to_dict()
        self.assertNotIn('trace_multiplier', data)


if __name__ == '__main__':
    unittest.main()
