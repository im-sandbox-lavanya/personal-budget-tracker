from collections import defaultdict


def get_monthly_summary(transactions, categories, year, month):
    """
    Return a summary dict for the given year/month:
      {
        "total_income": float,
        "total_expenses": float,
        "net_balance": float,
        "by_category": [{"name": str, "color": str, "amount": float}, ...]
      }
    """
    month_str = f"{year:04d}-{month:02d}"
    relevant = [t for t in transactions if t["date"].startswith(month_str)]

    total_income = sum(t["amount"] for t in relevant if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in relevant if t["type"] == "expense")
    net_balance = total_income - total_expenses

    cat_map = {c["id"]: c for c in categories}
    expense_by_cat = defaultdict(float)
    for t in relevant:
        if t["type"] == "expense":
            expense_by_cat[t["category_id"]] += t["amount"]

    by_category = []
    for cat_id, amount in sorted(expense_by_cat.items(), key=lambda x: -x[1]):
        cat = cat_map.get(cat_id, {"name": "Unknown", "color": "#6b7280"})
        by_category.append({"name": cat["name"], "color": cat["color"], "amount": amount})

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(net_balance, 2),
        "by_category": by_category,
    }


def enrich_transactions(transactions, categories):
    """Attach category name/color to each transaction for display."""
    cat_map = {c["id"]: c for c in categories}
    enriched = []
    for t in transactions:
        t = dict(t)
        cat = cat_map.get(t["category_id"], {"name": "Unknown", "color": "#6b7280"})
        t["category_name"] = cat["name"]
        t["category_color"] = cat["color"]
        enriched.append(t)
    return enriched


def filter_transactions(transactions, year=None, month=None, tx_type=None):
    result = transactions
    if year and month:
        month_str = f"{int(year):04d}-{int(month):02d}"
        result = [t for t in result if t["date"].startswith(month_str)]
    if tx_type in ("income", "expense"):
        result = [t for t in result if t["type"] == tx_type]
    return sorted(result, key=lambda t: t["date"], reverse=True)


def available_months(transactions):
    """Return sorted list of (year, month) tuples that have transactions."""
    months = sorted(
        {(int(t["date"][:4]), int(t["date"][5:7])) for t in transactions},
        reverse=True,
    )
    return months
