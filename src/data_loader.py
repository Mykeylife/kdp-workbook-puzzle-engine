import json
import os

def load_units_for_puzzles(json_path="data/units_en_fr.json"):
    """Loads units from JSON and returns {unit_title: [(en, fr), ...]} tuples."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, json_path)

    with open(full_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    formatted_units = {}
    for unit_title, items in raw_data.items():
        formatted_units[unit_title] = [(entry["en"], entry["fr"]) for entry in items]

    return formatted_units
