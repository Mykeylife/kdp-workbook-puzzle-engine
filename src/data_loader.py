import json
import os


def _resolve_path(json_path):
    """Resolves a relative path from the repository root."""
    if os.path.isabs(json_path):
        return json_path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, json_path)


def load_full_units(json_path="data/units_en_fr.json"):
    """Loads full unit objects including English, French/target word, and phonetics."""
    full_path = _resolve_path(json_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_units_for_puzzles(json_path="data/units_en_fr.json"):
    """Loads units from JSON and returns {unit_title: [(en, fr), ...]} tuples."""
    raw_data = load_full_units(json_path)
    formatted_units = {}
    for unit_title, items in raw_data.items():
        formatted_units[unit_title] = [(entry["en"], entry["fr"]) for entry in items]
    return formatted_units
    
