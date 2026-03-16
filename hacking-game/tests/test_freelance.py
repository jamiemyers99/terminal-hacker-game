"""Tests for missions/freelance.py — procedural briefing and system routing."""

import unittest

from missions.freelance import (
    _assemble_briefing,
    _pick_system_class,
    _CLIENTS,
    _TARGETS,
    _OBJECTIVES,
    _COMPLICATIONS,
)


class TestAssembleBriefing(unittest.TestCase):
    def _briefing(self):
        return _assemble_briefing('OmniTech Industries', 'internal data archive')

    def test_returns_non_empty_string(self):
        self.assertIsInstance(self._briefing(), str)
        self.assertGreater(len(self._briefing()), 0)

    def test_contains_target_name(self):
        self.assertIn('OmniTech Industries', self._briefing())

    def test_contains_target_type(self):
        self.assertIn('internal data archive', self._briefing())

    def test_briefing_varies(self):
        """Calling multiple times should (almost always) produce different text."""
        results = {_assemble_briefing('OmniTech Industries', 'archive')
                   for _ in range(30)}
        # With 10 clients × 10 objectives the chance of 30 identical results is negligible
        self.assertGreater(len(results), 1)


class TestFragmentPools(unittest.TestCase):
    def test_clients_non_empty(self):
        self.assertGreater(len(_CLIENTS), 0)

    def test_targets_non_empty(self):
        self.assertGreater(len(_TARGETS), 0)

    def test_objectives_non_empty(self):
        self.assertGreater(len(_OBJECTIVES), 0)

    def test_complications_non_empty(self):
        self.assertGreater(len(_COMPLICATIONS), 0)

    def test_each_target_is_two_tuple(self):
        for item in _TARGETS:
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)
            self.assertIsInstance(item[1], str)


class TestPickSystemClass(unittest.TestCase):
    def test_difficulty_1_is_corporate_server(self):
        from systems.corporate_server import CorporateServer
        self.assertIs(_pick_system_class(1), CorporateServer)

    def test_difficulty_2_is_bank_network(self):
        from systems.bank_network import BankNetwork
        self.assertIs(_pick_system_class(2), BankNetwork)

    def test_difficulty_3_is_military_firewall(self):
        from systems.military_firewall import MilitaryFirewall
        self.assertIs(_pick_system_class(3), MilitaryFirewall)

    def test_unknown_difficulty_defaults_to_corporate_server(self):
        from systems.corporate_server import CorporateServer
        self.assertIs(_pick_system_class(99), CorporateServer)


class TestFreelanceMissionInit(unittest.TestCase):
    def test_creates_mission_without_error(self):
        from engine.player import Player
        from missions.freelance import FreelanceMission
        p = Player('Ghost')
        m = FreelanceMission(p, difficulty=1)
        self.assertIsNotNone(m)

    def test_title_set_to_target_name(self):
        from engine.player import Player
        from missions.freelance import FreelanceMission
        p = Player('Ghost')
        m = FreelanceMission(p, difficulty=2)
        # Title should be one of the _TARGETS names in uppercase
        target_names = {name.upper() for name, _ in _TARGETS}
        self.assertIn(m.title, target_names)

    def test_narrative_intro_non_empty(self):
        from engine.player import Player
        from missions.freelance import FreelanceMission
        p = Player('Ghost')
        m = FreelanceMission(p, difficulty=1)
        self.assertGreater(len(m.narrative_intro), 0)

    def test_all_difficulties_construct(self):
        from engine.player import Player
        from missions.freelance import FreelanceMission
        for d in (1, 2, 3):
            p = Player('Ghost')
            m = FreelanceMission(p, difficulty=d)
            self.assertIsNotNone(m._system)


if __name__ == '__main__':
    unittest.main()
