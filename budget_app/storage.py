import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "budget.json")

DEFAULT_CATEGORIES = [
    {"id": str(uuid.uuid4()), "name": "Salary", "color": "#22c55e"},
    {"id": str(uuid.uuid4()), "name": "Food", "color": "#f97316"},
    {"id": str(uuid.uuid4()), "name": "Transport", "color": "#3b82f6"},
    {"id": str(uuid.uuid4()), "name": "Housing", "color": "#8b5cf6"},
    {"id": str(uuid.uuid4()), "name": "Healthcare", "color": "#ec4899"},
    {"id": str(uuid.uuid4()), "name": "Entertainment", "color": "#eab308"},
    {"id": str(uuid.uuid4()), "name": "Other", "color": "#6b7280"},
]


def _init_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        data = {"categories": DEFAULT_CATEGORIES, "transactions": []}
        _write_data(data)
    return _read_data()


def _read_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "categories" not in data:
            data["categories"] = []
        if "transactions" not in data:
            data["transactions"] = []
        return data
    except (json.JSONDecodeError, OSError):
        return {"categories": DEFAULT_CATEGORIES, "transactions": []}


def _write_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_data():
    if not os.path.exists(DATA_FILE):
        return _init_data_file()
    return _read_data()


# --- Categories ---

def get_categories():
    return load_data()["categories"]


def get_category_by_id(category_id):
    for cat in get_categories():
        if cat["id"] == category_id:
            return cat
    return None


def add_category(name, color="#6b7280"):
    data = load_data()
    new_cat = {"id": str(uuid.uuid4()), "name": name.strip(), "color": color}
    data["categories"].append(new_cat)
    _write_data(data)
    return new_cat


def delete_category(category_id):
    data = load_data()
    in_use = any(t["category_id"] == category_id for t in data["transactions"])
    if in_use:
        return False, "Cannot delete: category is used by existing transactions."
    data["categories"] = [c for c in data["categories"] if c["id"] != category_id]
    _write_data(data)
    return True, None


# --- Transactions ---

def get_transactions():
    return load_data()["transactions"]


def add_transaction(tx_type, amount, date, description, category_id):
    data = load_data()
    new_tx = {
        "id": str(uuid.uuid4()),
        "type": tx_type,
        "amount": round(float(amount), 2),
        "date": date,
        "description": description.strip(),
        "category_id": category_id,
        "created_at": datetime.utcnow().isoformat(),
    }
    data["transactions"].append(new_tx)
    _write_data(data)
    return new_tx


def delete_transaction(transaction_id):
    data = load_data()
    original_len = len(data["transactions"])
    data["transactions"] = [t for t in data["transactions"] if t["id"] != transaction_id]
    if len(data["transactions"]) < original_len:
        _write_data(data)
        return True
    return False
