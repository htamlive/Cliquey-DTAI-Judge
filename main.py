#!/usr/bin/env python3
"""
Entry point for the "botwar ship" game.
"""
import argparse
from runner import Runner


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="botwar ship - Hexagonal grid-based strategy game")
    parser.add_argument("--map", required=True, help="Path to the map JSON file")
    parser.add_argument("--agents", nargs=3, required=True, help="Paths to the three agent executables")
    parser.add_argument("--output", default="./data/logs/final_results.json", help="Output path for game logs")
    return parser.parse_args()


def main():
    """Main function to start the game."""
    args = parse_args()

    # Initialize the runner with the agents
    runner = Runner(args.agents)

    # Initialize the game with the map
    runner.initialize_game(args.map, args.output)

    # Run the game until completion
    runner.run_game()

    # Report the final results
    runner.report_results()


if __name__ == "__main__":
    main()
