"""A small deterministic, turn-based terminal adventure. Standard library only."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import random

MONSTERS = (("Suspicious sock", 9), ("Tax-return goblin", 13), ("The office printer", 18))

@dataclass(frozen=True)
class State:
    seed: int = 42
    hp: int = 24
    potions: int = 2
    room: int = 0
    enemy_hp: int = 9
    turn: int = 0

    @property
    def status(self) -> str:
        return "lost" if self.hp == 0 else "won" if self.room == len(MONSTERS) else "playing"

def step(state: State, action: str) -> tuple[State, list[str]]:
    if action not in ("attack", "guard", "potion"):
        raise ValueError("Choose attack, guard or potion.")
    if state.status != "playing":
        return state, ["This adventure is over."]
    if action == "potion" and (state.potions == 0 or state.hp == 24):
        return state, ["No potion needed or available. Your turn was not used."]
    # Each turn has its own seeded random stream, so a JSON save can resume exactly.
    rng = random.Random(f"{state.seed}:{state.turn}")
    hp, enemy_hp, potions = state.hp, state.enemy_hp, state.potions
    messages = []
    if action == "attack":
        damage = rng.randint(4, 9)
        enemy_hp = max(0, enemy_hp - damage)
        messages.append(f"You hit for {damage}.")
    elif action == "guard":
        damage = rng.randint(1, 3)
        enemy_hp = max(0, enemy_hp - damage)
        messages.append(f"You guard and counter for {damage}.")
    else:
        hp = min(24, hp + 10)
        potions -= 1
        messages.append("Potion used: up to 10 HP restored.")
    if enemy_hp == 0:
        room = state.room + 1
        messages.append(f"Defeated {MONSTERS[state.room][0]}!")
        return replace(state, hp=min(24, hp + 3), potions=potions, room=room,
                       enemy_hp=MONSTERS[room][1] if room < len(MONSTERS) else 0,
                       turn=state.turn + 1), messages
    incoming = rng.randint(2, 6)
    if action == "guard":
        incoming = max(1, incoming // 3)
    hp = max(0, hp - incoming)
    messages.append(f"The enemy hits for {incoming}.")
    return replace(state, hp=hp, enemy_hp=enemy_hp, potions=potions, turn=state.turn + 1), messages

def save(state: State, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps({"version": 1, "state": asdict(state)}, indent=2) + "\n", encoding="utf8")
    temporary.replace(path)

def load(path: Path) -> State:
    if path.stat().st_size > 4096:
        raise ValueError("Save file is too large.")
    value = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(value, dict) or value.get("version") != 1 or not isinstance(value.get("state"), dict):
        raise ValueError("Unsupported save format.")
    data = value["state"]
    if set(data) != set(State.__dataclass_fields__) or any(type(v) is not int for v in data.values()):
        raise ValueError("Invalid save fields.")
    state = State(**data)
    if not (0 <= state.hp <= 24 and 0 <= state.potions <= 2 and 0 <= state.room <= len(MONSTERS)
            and 0 <= state.turn <= 1_000_000 and -(2**63) <= state.seed < 2**63):
        raise ValueError("Invalid save values.")
    if state.room == len(MONSTERS):
        valid_enemy = state.enemy_hp == 0 and state.hp > 0
    else:
        valid_enemy = 1 <= state.enemy_hp <= MONSTERS[state.room][1]
    if not valid_enemy:
        raise ValueError("Invalid enemy state.")
    return state

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--save", type=Path, default=Path("adventure.json"))
    parser.add_argument("--demo", action="store_true", help="Run an automatic sample without prompts.")
    args = parser.parse_args()
    try:
        if not -(2**63) <= args.seed < 2**63:
            raise ValueError("Seed must be a signed 64-bit integer.")
        state = load(args.resume) if args.resume else State(seed=args.seed)
        print("DICE DUNGEON — one sock, one goblin, one very angry printer")
        while state.status == "playing":
            print(f"\nRoom {state.room + 1}: {MONSTERS[state.room][0]} ({state.enemy_hp} HP) | You: {state.hp} HP, {state.potions} potions")
            if args.demo:
                action = "potion" if state.hp <= 12 and state.potions else "attack"
            else:
                try:
                    action = input("[a]ttack [g]uard [p]otion [s]ave & quit: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    action = "s"
                if action == "s":
                    save(state, args.save)
                    print(f"Saved to {args.save}.")
                    return 0
                action = {"a": "attack", "g": "guard", "p": "potion"}.get(action, action)
            try:
                state, messages = step(state, action)
                print(" ".join(messages))
            except ValueError as error:
                print(error)
        print("\nVictory! The printer finally works." if state.status == "won" else "\nThe dungeon wins. Try another seed.")
        return 0
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"Error: {error}\n")

if __name__ == "__main__":
    raise SystemExit(main())
