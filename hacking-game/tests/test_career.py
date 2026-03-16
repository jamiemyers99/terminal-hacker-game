"""Tests for engine/career.py — cross-session career stat accumulation."""

import os
import tempfile
import unittest
from unittest.mock import patch

from engine.player import Player
import engine.career as cr


class TestCareer(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            suffix='.json', delete=False
        )
        self._tmp.close()
        os.unlink(self._tmp.name)
        self._patcher = patch.object(cr, 'CAREER_PATH', self._tmp.name)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def _player(self, credits=0, tools=None):
        p = Player('Ghost')
        p.credits = credits
        if tools:
            for t in tools:
                p.add_tool(t)
        return p

    # ── load_career ───────────────────────────────────────────────────────────

    def test_load_career_defaults_when_no_file(self):
        stats = cr.load_career()
        self.assertEqual(stats['story_runs'], 0)
        self.assertEqual(stats['freelance_runs'], 0)
        self.assertEqual(stats['lifetime_credits'], 0)
        self.assertEqual(stats['endings']['ghost'], 0)
        self.assertEqual(stats['endings']['chaos'], 0)

    # ── record_run ────────────────────────────────────────────────────────────

    def test_story_run_increments_story_runs(self):
        cr.record_run(self._player(), mode='story')
        self.assertEqual(cr.load_career()['story_runs'], 1)

    def test_freelance_run_increments_freelance_runs(self):
        cr.record_run(self._player(), mode='freelance-1')
        stats = cr.load_career()
        self.assertEqual(stats['freelance_runs'], 1)
        self.assertEqual(stats['story_runs'], 0)

    def test_credits_accumulated(self):
        cr.record_run(self._player(credits=1000), mode='story')
        cr.record_run(self._player(credits=500),  mode='story')
        self.assertEqual(cr.load_career()['lifetime_credits'], 1500)

    def test_best_run_tracks_maximum(self):
        cr.record_run(self._player(credits=1000), mode='story')
        cr.record_run(self._player(credits=3000), mode='story')
        cr.record_run(self._player(credits=500),  mode='story')
        self.assertEqual(cr.load_career()['best_run'], 3000)

    def test_tools_collected_accumulates(self):
        cr.record_run(self._player(tools=['port_scanner', 'vpn_shield']), mode='story')
        cr.record_run(self._player(tools=['root_kit']), mode='story')
        self.assertEqual(cr.load_career()['tools_collected'], 3)

    def test_missions_done_accumulates(self):
        cr.record_run(self._player(), mode='story', missions_done=4)
        cr.record_run(self._player(), mode='story', missions_done=2)
        self.assertEqual(cr.load_career()['missions_done'], 6)

    def test_ghost_ending_recorded(self):
        cr.record_run(self._player(), mode='story', ending='ghost')
        self.assertEqual(cr.load_career()['endings']['ghost'], 1)

    def test_chaos_ending_recorded(self):
        cr.record_run(self._player(), mode='story', ending='chaos')
        self.assertEqual(cr.load_career()['endings']['chaos'], 1)

    def test_unknown_ending_ignored(self):
        cr.record_run(self._player(), mode='story', ending='banana')
        stats = cr.load_career()
        self.assertEqual(stats['endings']['ghost'], 0)
        self.assertEqual(stats['endings']['chaos'], 0)

    def test_multiple_runs_accumulate(self):
        for _ in range(5):
            cr.record_run(self._player(), mode='story')
        self.assertEqual(cr.load_career()['story_runs'], 5)

    def test_back_fill_missing_keys(self):
        """load_career() adds missing keys from _DEFAULTS for older save files."""
        import json
        # Write a career file that's missing newer keys
        os.makedirs(os.path.dirname(cr.CAREER_PATH), exist_ok=True)
        with open(cr.CAREER_PATH, 'w') as f:
            json.dump({'story_runs': 3}, f)

        stats = cr.load_career()
        self.assertEqual(stats['story_runs'], 3)
        self.assertIn('freelance_runs', stats)
        self.assertIn('lifetime_credits', stats)


if __name__ == '__main__':
    unittest.main()
