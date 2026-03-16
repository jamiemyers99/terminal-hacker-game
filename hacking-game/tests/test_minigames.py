"""Tests for minigame logic (pure functions only — no I/O)."""

import unittest

from minigames.sequence_decoder import _make_grid, _make_solvable_target
from minigames.firewall_maze    import _generate_maze


# ---------------------------------------------------------------------------
# Sequence decoder — grid & puzzle generation
# ---------------------------------------------------------------------------

class TestSequenceDecoderGrid(unittest.TestCase):
    def test_grid_dimensions_4x4(self):
        grid = _make_grid(4)
        self.assertEqual(len(grid), 4)
        for row in grid:
            self.assertEqual(len(row), 4)

    def test_grid_dimensions_5x5(self):
        grid = _make_grid(5)
        self.assertEqual(len(grid), 5)
        for row in grid:
            self.assertEqual(len(row), 5)

    def test_grid_values_from_hex_pool(self):
        from minigames.sequence_decoder import _HEX_POOL
        grid = _make_grid(4)
        for row in grid:
            for val in row:
                self.assertIn(val, _HEX_POOL)


class TestMakeSolvableTarget(unittest.TestCase):
    def _run(self, size, target_len):
        grid   = _make_grid(size)
        target, path = _make_solvable_target(grid, target_len)
        return grid, target, path

    def test_target_length_matches_request(self):
        _, target, _ = self._run(4, 3)
        self.assertEqual(len(target), 3)

    def test_path_length_matches_target(self):
        _, target, path = self._run(5, 4)
        self.assertEqual(len(path), len(target))

    def test_path_values_match_grid(self):
        grid, target, path = self._run(4, 3)
        for i, (r, c) in enumerate(path):
            self.assertEqual(grid[r][c], target[i])

    def test_alternating_constraint_respected(self):
        """Even steps fix row; odd steps fix column."""
        grid, _, path = self._run(5, 4)
        for step in range(1, len(path)):
            prev_r, prev_c = path[step - 1]
            curr_r, curr_c = path[step]
            if step % 2 == 1:   # odd → picked a row from prev column
                self.assertEqual(curr_c, prev_c,
                    f"Step {step} should share column with step {step-1}")
            else:               # even → picked a column from prev row
                self.assertEqual(curr_r, prev_r,
                    f"Step {step} should share row with step {step-1}")

    def test_all_path_coordinates_in_bounds(self):
        size = 4
        grid, _, path = self._run(size, 3)
        for r, c in path:
            self.assertGreaterEqual(r, 0)
            self.assertLess(r, size)
            self.assertGreaterEqual(c, 0)
            self.assertLess(c, size)

    def test_first_step_is_in_row_0(self):
        """Path always starts from row 0 (even step = pick column from active row)."""
        for _ in range(10):     # run several times due to randomness
            grid, _, path = self._run(4, 3)
            self.assertEqual(path[0][0], 0)


# ---------------------------------------------------------------------------
# Firewall maze — DFS generation and connectivity
# ---------------------------------------------------------------------------

class TestFirewallMaze(unittest.TestCase):
    def _maze_dims(self, rows, cols):
        """Return expected rendered dimensions for a cells×cells maze."""
        return rows * 2 + 1, cols * 2 + 1

    def test_maze_correct_dimensions(self):
        rows, cols = 5, 5
        maze = _generate_maze(rows, cols)
        h, w = self._maze_dims(rows, cols)
        self.assertEqual(len(maze), h)
        for row in maze:
            self.assertEqual(len(row), w)

    def test_maze_contains_only_valid_chars(self):
        maze = _generate_maze(5, 5)
        for row in maze:
            for cell in row:
                self.assertIn(cell, ('#', ' '))

    def test_start_cell_is_open(self):
        maze = _generate_maze(5, 5)
        # Cell (0,0) in maze coordinates → rendered position (1,1)
        self.assertEqual(maze[1][1], ' ')

    def test_exit_cell_is_open(self):
        rows, cols = 5, 5
        maze = _generate_maze(rows, cols)
        # Bottom-right cell → rendered position (rows*2-1, cols*2-1)
        self.assertEqual(maze[rows * 2 - 1][cols * 2 - 1], ' ')

    def test_exit_reachable_from_start_bfs(self):
        """BFS from start must reach the exit — maze must be fully connected."""
        from collections import deque
        rows, cols = 7, 7
        maze = _generate_maze(rows, cols)
        h    = len(maze)
        w    = len(maze[0])

        start = (1, 1)
        goal  = (h - 2, w - 2)

        visited = set()
        queue   = deque([start])
        visited.add(start)

        while queue:
            r, c = queue.popleft()
            if (r, c) == goal:
                self.assertTrue(True)
                return
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < h and 0 <= nc < w
                        and maze[nr][nc] == ' '
                        and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

        self.fail("Exit is not reachable from start — maze is disconnected.")

    def test_different_sizes(self):
        for rows, cols in [(5, 5), (7, 7), (9, 9)]:
            maze = _generate_maze(rows, cols)
            self.assertEqual(len(maze), rows * 2 + 1)


if __name__ == '__main__':
    unittest.main()
