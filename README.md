# Dice Dungeon — Python terminal game

Fight a suspicious sock, a tax-return goblin and an office printer. A small, deliberately ridiculous turn-based adventure using only the Python standard library. **New portfolio example.** This is not recovered source from an older role-playing project.

## Run

Python 3.12+; no dependencies.

```sh
python dungeon.py
python dungeon.py --seed 123
python dungeon.py --demo
python dungeon.py --resume adventure.json
```

Attack for damage, guard to reduce incoming damage, or use a limited healing potion. Defeating an enemy restores 3 HP. Press `s` to save and quit. A fixed seed plus the same choices gives the same adventure; changing the seed gives a different run. Terminal outcomes are printed and exit successfully; invalid files/options exit with code 2.

## Implementation

- Frozen dataclass state and a pure turn-transition function.
- Explicit playing/won/lost states and bounded health/potion values.
- Per-turn deterministic random streams, including after save/resume.
- Versioned JSON saves, validated fields and atomic same-directory replacement.
- `argparse` CLI with an automated demo mode.

```sh
python -m unittest discover -s tests -v
```

Six tests cover reproducibility, combat transitions, potion limits, terminal states, exact save/resume and invalid input. Save files are for local convenience; editing a valid save is not prevented.
