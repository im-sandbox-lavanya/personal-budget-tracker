from datetime import datetime

VALID_TYPES = ("income", "expense")


def validate_transaction(form_data, categories):
    errors = {}

    tx_type = form_data.get("type", "").strip()
    if tx_type not in VALID_TYPES:
        errors["type"] = "Type must be 'income' or 'expense'."

    amount_raw = form_data.get("amount", "").strip()
    if not amount_raw:
        errors["amount"] = "Amount is required."
    else:
        try:
            amount = float(amount_raw)
            if amount <= 0:
                errors["amount"] = "Amount must be greater than zero."
        except ValueError:
            errors["amount"] = "Amount must be a valid number."

    date_raw = form_data.get("date", "").strip()
    if not date_raw:
        errors["date"] = "Date is required."
    else:
        try:
            datetime.strptime(date_raw, "%Y-%m-%d")
        except ValueError:
            errors["date"] = "Date must be in YYYY-MM-DD format."

    description = form_data.get("description", "").strip()
    if not description:
        errors["description"] = "Description is required."
    elif len(description) > 200:
        errors["description"] = "Description must be 200 characters or fewer."

    category_id = form_data.get("category_id", "").strip()
    if not category_id:
        errors["category_id"] = "Category is required."
    else:
        valid_ids = {c["id"] for c in categories}
        if category_id not in valid_ids:
            errors["category_id"] = "Selected category does not exist."

    return errors


def validate_category(form_data, existing_categories):
    errors = {}

    name = form_data.get("name", "").strip()
    if not name:
        errors["name"] = "Category name is required."
    elif len(name) > 50:
        errors["name"] = "Category name must be 50 characters or fewer."
    else:
        existing_names = {c["name"].lower() for c in existing_categories}
        if name.lower() in existing_names:
            errors["name"] = f"A category named '{name}' already exists."

    return errors
