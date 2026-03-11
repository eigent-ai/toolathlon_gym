#!/usr/bin/env python3
"""Filter recipes by difficulty level.
Usage: python filter_recipes.py recipes.json --max-difficulty 3
Outputs filtered recipes as JSON to stdout.
"""
import json
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="Filter recipes by difficulty level")
    parser.add_argument("input_file", help="JSON file with recipes")
    parser.add_argument("--max-difficulty", type=int, default=3,
                        help="Maximum difficulty level to include (default: 3)")
    args = parser.parse_args()

    with open(args.input_file) as f:
        recipes = json.load(f)

    filtered = [r for r in recipes if r.get("difficulty", 5) <= args.max_difficulty]
    print(json.dumps(filtered, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
