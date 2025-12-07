import os
import argparse

from .robotics.grid_world import GridWorld
from .robotics.astar import astar
from .ml.q_learning import GridWorldEnv, QLearningAgent, MultiAgentQLearning
from .vision.color_detect import run_demo
from .security.crypto_utils import generate_key, encrypt, decrypt, sha256_hash


def ensure_artifacts() -> str:
    here = os.path.dirname(__file__)
    d = os.path.join(here, "artifacts")
    os.makedirs(d, exist_ok=True)
    return d


def sample_grid() -> GridWorld:
    width, height = 5, 5
    obstacles = {(x, 2) for x in range(5) if x != 2}
    start, goal = (0, 0), (4, 4)
    return GridWorld(width, height, obstacles, start, goal)


def cmd_plan() -> None:
    grid = sample_grid()
    path = astar(grid)
    artifacts = ensure_artifacts()
    out = os.path.join(artifacts, "astar_path.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join([f"{p[0]},{p[1]}" for p in path]))
    print(f"A* path length: {max(0, len(path) - 1)}")
    print(f"Saved path to {out}")


def cmd_multi_qlearn() -> None:
    grid = sample_grid()
    env = GridWorldEnv(grid, max_steps=200, seed=789)
    multi_agent = MultiAgentQLearning(env, num_agents=3, seed=789)
    multi_agent.train_agents(episodes=500, max_steps_per_episode=200)
    path = multi_agent.derive_consensus_path(start=grid.start, max_steps=100)
    artifacts = ensure_artifacts()
    out = os.path.join(artifacts, "multi_qlearn_path.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join([f"{p[0]},{p[1]}" for p in path]))
    print(f"Multi-agent Q-learning path length: {max(0, len(path) - 1)}")
    print(f"Saved consensus path to {out}")


def cmd_vision() -> None:
    artifacts = ensure_artifacts()
    out = run_demo(output_dir=artifacts)
    print(f"Saved color detection demo to {out}")


def cmd_crypto() -> None:
    artifacts = ensure_artifacts()
    key = generate_key()
    message = b"Hello TU Ilmenau - CS & Automation"
    token = encrypt(message, key)
    decoded = decrypt(token, key)
    h = sha256_hash(message)

    with open(os.path.join(artifacts, "secret.bin"), "wb") as f:
        f.write(token)
    with open(os.path.join(artifacts, "secret.txt"), "wb") as f:
        f.write(decoded)
    with open(os.path.join(artifacts, "hash.txt"), "w", encoding="utf-8") as f:
        f.write(h)

    print(f"Encrypted roundtrip ok: {decoded == message}")
    print(f"SHA-256: {h}")


def main() -> None:
    parser = argparse.ArgumentParser(description="CS Automation Capstone demos")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    sub.add_parser("qlearn")
    sub.add_parser("multi_qlearn")
    sub.add_parser("vision")
    sub.add_parser("crypto")
    args = parser.parse_args()

    if args.cmd == "plan":
        cmd_plan()
    elif args.cmd == "qlearn":
        cmd_qlearn()
    elif args.cmd == "multi_qlearn":
        cmd_multi_qlearn()
    elif args.cmd == "vision":
        cmd_vision()
    elif args.cmd == "crypto":
        cmd_crypto()


if __name__ == "__main__":
    main()
