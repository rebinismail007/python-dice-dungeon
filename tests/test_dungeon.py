import json
from pathlib import Path
import tempfile
import unittest
from dungeon import State, load, save, step

class DungeonTests(unittest.TestCase):
    def test_same_seed_and_actions_are_reproducible(self):
        self.assertEqual(step(State(seed=7), "attack"), step(State(seed=7), "attack"))

    def test_defeated_enemy_does_not_retaliate(self):
        after, _ = step(State(hp=10, enemy_hp=1), "attack")
        self.assertEqual((after.room, after.enemy_hp, after.hp), (1, 13, 13))

    def test_no_potion_or_full_health_does_not_use_a_turn(self):
        for state in (State(), State(hp=10, potions=0)):
            self.assertEqual(step(state, "potion")[0], state)

    def test_terminal_states_are_locked(self):
        for state in (State(hp=0), State(room=3, enemy_hp=0)):
            self.assertEqual(step(state, "attack")[0], state)

    def test_save_resume_continues_the_identical_random_stream(self):
        state, _ = step(State(seed=123), "guard")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            save(state, path)
            self.assertEqual(load(path), state)
            self.assertEqual(step(load(path), "attack"), step(state, "attack"))

    def test_corrupted_save_and_invalid_actions_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            for data in ({"version": 1, "state": {"hp": 999}}, {"version": 2}, []):
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError): load(path)
        with self.assertRaises(ValueError): step(State(), "teleport")

if __name__ == "__main__":
    unittest.main()
