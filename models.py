from datetime import date
import csv
from pathlib import Path

USD_PER_WAR = {
    "pre_arb": 0,
    "arb": 2_500_000,
    "fa": 9_000_000
}

LEAGUE_MIN = 740_000
DATA_PATH = Path("data/players.csv")

STATUS_LABEL = {
    "pre_arb": "Pre-Arb",
    "arb": "Arbitration",
    "fa": "Free Agency"
}

def season_bounds(year: int):
    return date(year, 3, 28), date(year, 9, 29)

def days_elapsed_in_season(today: date):
    start, end = season_bounds(today.year)
    if today < start:
        return 0
    if today > end:
        return (end - start).days + 1
    return (today - start).days + 1

def _load_row(name: str, year: int):
    name_l = name.strip().lower()
    if not DATA_PATH.exists():
        return None
    with DATA_PATH.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["player"].strip().lower() == name_l:
                if year == 2025:
                    return {
                        "player": row["player"],
                        "team": row.get("team", ""),
                        "status": row["status"].strip().lower(),
                        "salary": int(float(row["salary"])),
                        "war": float(row["war_2025"]),
                        "pa": int(float(row["pa_2025"])),
                        "g": int(float(row["g_2025"])),
                    }
    return None

def _performance_label(delta: int):
    if delta > 0:
        return "above value"
    if delta < 0:
        return "below value"
    return "exactly at value"

def _performance_adverb(delta: int) -> str:
    if delta > 0:
        return "well"
    if delta < 0:
        return "badly"
    return "exactly at value"

def compute_value_row(name: str, year: int, today: date | None = None):
    today = today or date.today()
    base = _load_row(name, year)
    if not base:
        return None

    status = base["status"]
    usd_per_war = USD_PER_WAR.get(status, USD_PER_WAR["fa"])
    war = base["war"]
    salary = base["salary"]
    pa = max(1, base["pa"])
    g = max(1, base["g"])

    market_value = war * usd_per_war
    days = max(1, days_elapsed_in_season(today))

    value_per_day = market_value / days
    value_per_game = market_value / g
    value_per_pa = market_value / pa

    delta = market_value - salary
    owes_mode = market_value < 0

    performance_status = _performance_label(int(round(delta)))
    performance_word = _performance_adverb(int(round(delta)))
    status_label = STATUS_LABEL.get(status, status.title())

    return {
        "player": base["player"],
        "team": base["team"],
        "year": year,
        "status": status,
        "status_label": status_label,
        "usd_per_war": int(usd_per_war),
        "war": round(war, 2),
        "pa": pa,
        "games": g,
        "days_elapsed": days,
        "actual_salary": int(round(salary)),
        "market_value": int(round(market_value)),
        "value_per_day": int(round(value_per_day)),
        "value_per_game": int(round(value_per_game)),
        "value_per_pa": int(round(value_per_pa)),
        "delta": int(round(delta)),
        "performance_status": performance_status,
        "performance_word": performance_word,
        "owes_mode": owes_mode
    }
