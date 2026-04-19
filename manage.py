"""
CLI for managing DailyNewsBrief preferences.

Usage:
  python manage.py list
  python manage.py follow topic "AI"
  python manage.py unfollow topic "cybersecurity"
  python manage.py follow sport "F1"
  python manage.py unfollow sport "Cricket"
  python manage.py follow team "Warriors" --sport NBA
  python manage.py unfollow team "Warriors"
  python manage.py follow stock "AAPL"
  python manage.py unfollow stock "NVDA"
"""

import argparse
import sys
import os
import yaml

PREFS_PATH = os.path.join(os.path.dirname(__file__), "preferences.yaml")


def load() -> dict:
    with open(PREFS_PATH) as f:
        return yaml.safe_load(f)


def save(prefs: dict):
    with open(PREFS_PATH, "w") as f:
        yaml.dump(prefs, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def cmd_list(prefs: dict, _args):
    print("\n=== Tech Topics ===")
    for t in prefs.get("tech_topics", []):
        print(f"  • {t}")

    print("\n=== Sports ===")
    for s in prefs.get("sports", []):
        teams = s.get("teams", [])
        team_str = f"  → teams: {', '.join(teams)}" if teams else ""
        print(f"  • {s['sport']}{team_str}")

    print("\n=== Stocks ===")
    for ticker in prefs.get("stocks", []):
        print(f"  • {ticker}")

    print()


def cmd_follow(prefs: dict, args):
    category = args.category
    value = args.value

    if category == "topic":
        topics = prefs.setdefault("tech_topics", [])
        if value in topics:
            print(f"Already following topic: {value}")
        else:
            topics.append(value)
            save(prefs)
            print(f"Following topic: {value}")

    elif category == "sport":
        sports = prefs.setdefault("sports", [])
        if any(s["sport"] == value for s in sports):
            print(f"Already following sport: {value}")
        else:
            sports.append({"sport": value})
            save(prefs)
            print(f"Following sport: {value}")

    elif category == "team":
        if not args.sport:
            print("Error: --sport is required when following a team (e.g. --sport NBA)")
            sys.exit(1)
        sports = prefs.setdefault("sports", [])
        sport_entry = next((s for s in sports if s["sport"] == args.sport), None)
        if sport_entry is None:
            sports.append({"sport": args.sport, "teams": [value]})
            save(prefs)
            print(f"Added {args.sport} and following team: {value}")
        else:
            teams = sport_entry.setdefault("teams", [])
            if value in teams:
                print(f"Already following team: {value}")
            else:
                teams.append(value)
                save(prefs)
                print(f"Following team: {value} ({args.sport})")

    elif category == "stock":
        stocks = prefs.setdefault("stocks", [])
        ticker = value.upper()
        if ticker in stocks:
            print(f"Already following stock: {ticker}")
        else:
            stocks.append(ticker)
            save(prefs)
            print(f"Following stock: {ticker}")

    else:
        print(f"Unknown category: {category}. Use: topic, sport, team, stock")
        sys.exit(1)


def cmd_unfollow(prefs: dict, args):
    category = args.category
    value = args.value

    if category == "topic":
        topics = prefs.get("tech_topics", [])
        if value not in topics:
            print(f"Not following topic: {value}")
        else:
            topics.remove(value)
            save(prefs)
            print(f"Unfollowed topic: {value}")

    elif category == "sport":
        sports = prefs.get("sports", [])
        entry = next((s for s in sports if s["sport"] == value), None)
        if entry is None:
            print(f"Not following sport: {value}")
        else:
            sports.remove(entry)
            save(prefs)
            print(f"Unfollowed sport: {value} (and all its teams)")

    elif category == "team":
        sports = prefs.get("sports", [])
        removed = False
        for sport_entry in sports:
            teams = sport_entry.get("teams", [])
            if value in teams:
                teams.remove(value)
                save(prefs)
                print(f"Unfollowed team: {value} ({sport_entry['sport']})")
                removed = True
                break
        if not removed:
            print(f"Not following team: {value}")

    elif category == "stock":
        stocks = prefs.get("stocks", [])
        ticker = value.upper()
        if ticker not in stocks:
            print(f"Not following stock: {ticker}")
        else:
            stocks.remove(ticker)
            save(prefs)
            print(f"Unfollowed stock: {ticker}")

    else:
        print(f"Unknown category: {category}. Use: topic, sport, team, stock")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Manage DailyNewsBrief preferences",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Show all current preferences")

    for cmd_name in ("follow", "unfollow"):
        p = subparsers.add_parser(cmd_name, help=f"{cmd_name.capitalize()} a topic/sport/team/stock")
        p.add_argument("category", choices=["topic", "sport", "team", "stock"])
        p.add_argument("value", help="Name of the topic, sport, team, or stock ticker")
        p.add_argument("--sport", help="Sport name (required when category is 'team')")

    args = parser.parse_args()
    prefs = load()

    if args.command == "list":
        cmd_list(prefs, args)
    elif args.command == "follow":
        cmd_follow(prefs, args)
    elif args.command == "unfollow":
        cmd_unfollow(prefs, args)


if __name__ == "__main__":
    main()
