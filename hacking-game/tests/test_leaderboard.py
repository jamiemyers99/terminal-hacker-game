"""Tests for engine/leaderboard.py — high score persistence."""

import os
import tempfile
import unittest
from unittest.mock import patch

import engine.leaderboard as lb


class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            suffix='.json', delete=False
        )
        self._tmp.close()
        # Remove it so load_scores() treats it as "no file yet"
        os.unlink(self._tmp.name)
        self._patcher = patch.object(lb, 'LEADERBOARD_PATH', self._tmp.name)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    # ── load_scores ───────────────────────────────────────────────────────────

    def test_load_scores_empty_when_no_file(self):
        self.assertEqual(lb.load_scores(), [])

    # ── add_entry ─────────────────────────────────────────────────────────────

    def test_add_first_entry_returns_rank_1(self):
        rank = lb.add_entry('Ghost', 1000, 4, 'story')
        self.assertEqual(rank, 1)

    def test_add_entry_stored(self):
        lb.add_entry('Ghost', 1000, 4, 'story')
        entries = lb.load_scores()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['alias'], 'Ghost')
        self.assertEqual(entries[0]['score'], 1000)

    def test_entries_sorted_highest_first(self):
        lb.add_entry('Low',  500,  1, 'story')
        lb.add_entry('High', 9000, 4, 'story')
        lb.add_entry('Mid',  2500, 2, 'story')

        entries = lb.load_scores()
        scores = [e['score'] for e in entries]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_max_entries_capped(self):
        for i in range(lb.MAX_ENTRIES + 5):
            lb.add_entry(f'P{i}', i * 100, 0, 'story')

        entries = lb.load_scores()
        self.assertLessEqual(len(entries), lb.MAX_ENTRIES)

    def test_alias_truncated_to_16_chars(self):
        lb.add_entry('A' * 30, 500, 0, 'story')
        entries = lb.load_scores()
        self.assertLessEqual(len(entries[0]['alias']), 16)

    def test_mode_stored(self):
        lb.add_entry('Ghost', 800, 0, 'freelance-2')
        entries = lb.load_scores()
        self.assertEqual(entries[0]['mode'], 'freelance-2')

    # ── is_high_score ─────────────────────────────────────────────────────────

    def test_is_high_score_when_board_empty(self):
        self.assertTrue(lb.is_high_score(1))

    def test_is_high_score_true_when_board_not_full(self):
        lb.add_entry('Ghost', 500, 0, 'story')
        self.assertTrue(lb.is_high_score(1))   # board not at MAX_ENTRIES yet

    def test_is_high_score_false_when_below_last(self):
        for i in range(lb.MAX_ENTRIES):
            lb.add_entry(f'P{i}', (i + 1) * 1000, 0, 'story')
        # Lowest score on a full board = 1000; submitting 500 should fail
        self.assertFalse(lb.is_high_score(500))

    def test_is_high_score_true_when_above_last(self):
        for i in range(lb.MAX_ENTRIES):
            lb.add_entry(f'P{i}', (i + 1) * 100, 0, 'story')
        # Highest score = MAX_ENTRIES*100; submitting above that qualifies
        self.assertTrue(lb.is_high_score(lb.MAX_ENTRIES * 100 + 1))


if __name__ == '__main__':
    unittest.main()
