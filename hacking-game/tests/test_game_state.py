"""Tests for engine/game_state.py — save / load / delete."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from engine.player import Player
import engine.game_state as gs


class TestGameState(unittest.TestCase):
    def setUp(self):
        # Redirect all file I/O to a temp file for each test
        self._tmp = tempfile.NamedTemporaryFile(
            suffix='.json', delete=False
        )
        self._tmp.close()
        self._path_patcher = patch.object(gs, 'SAVE_PATH', self._tmp.name)
        self._path_patcher.start()

    def tearDown(self):
        self._path_patcher.stop()
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    # ── save_game ─────────────────────────────────────────────────────────────

    def test_save_creates_file(self):
        p = Player('Ghost')
        gs.save_game(p, 'mission_1')
        self.assertTrue(os.path.exists(gs.SAVE_PATH))

    def test_save_content(self):
        p = Player('Spectre')
        p.credits = 1000
        gs.save_game(p, 'mission_2')

        with open(gs.SAVE_PATH, encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data['current_mission'], 'mission_2')
        self.assertEqual(data['player']['name'], 'Spectre')
        self.assertEqual(data['player']['credits'], 1000)

    # ── load_game ─────────────────────────────────────────────────────────────

    def test_load_returns_none_when_no_file(self):
        os.unlink(gs.SAVE_PATH)
        self.assertIsNone(gs.load_game())

    def test_load_returns_none_on_corrupt_json(self):
        with open(gs.SAVE_PATH, 'w') as f:
            f.write('not json {{{{')
        self.assertIsNone(gs.load_game())

    def test_load_round_trip(self):
        p = Player('Wraith')
        p.level = 2
        p.add_tool('port_scanner')
        gs.save_game(p, 'mission_3')

        data = gs.load_game()
        self.assertIsNotNone(data)
        restored = Player.from_dict(data['player'])
        self.assertEqual(restored.name, 'Wraith')
        self.assertEqual(restored.level, 2)
        self.assertIn('port_scanner', restored.tools)
        self.assertEqual(data['current_mission'], 'mission_3')

    # ── delete_save ───────────────────────────────────────────────────────────

    def test_delete_returns_true_when_file_exists(self):
        p = Player('Ghost')
        gs.save_game(p, 'mission_1')
        self.assertTrue(gs.delete_save())
        self.assertFalse(os.path.exists(gs.SAVE_PATH))

    def test_delete_returns_false_when_no_file(self):
        os.unlink(gs.SAVE_PATH)
        self.assertFalse(gs.delete_save())

    # ── save_exists ───────────────────────────────────────────────────────────

    def test_save_exists_true(self):
        p = Player('Ghost')
        gs.save_game(p, 'mission_1')
        self.assertTrue(gs.save_exists())

    def test_save_exists_false(self):
        os.unlink(gs.SAVE_PATH)
        self.assertFalse(gs.save_exists())


if __name__ == '__main__':
    unittest.main()
