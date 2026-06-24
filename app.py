import csv
import io
from datetime import datetime

from flask import Flask, Response, flash, redirect, render_template, request, url_for

from budget_app import models, services, storage

app = Flask(__name__)
app.secret_key = "budget-tracker-secret-key-local-only"

# Ensure data file is initialized on startup
storage.load_data()


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------

def _current_month_year():
    now = datetime.today()
    return now.year, now.month


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    year = int(request.args.get("year", datetime.today().year))
    month = int(request.args.get("month", datetime.today().month))

    data = storage.load_data()
    transactions = data["transactions"]
    categories = data["categories"]

    summary = services.get_monthly_summary(transactions, categories, year, month)
    recent = services.filter_transactions(transactions, year=year, month=month)
    recent = services.enrich_transactions(recent[:10], categories)
    months = services.available_months(transactions)

    return render_template(
        "dashboard.html",
        summary=summary,
        recent=recent,
        months=months,
        selected_year=year,
        selected_month=month,
        month_name=datetime(year, month, 1).strftime("%B %Y"),
    )


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@app.route("/transactions")
def transactions():
    year_param = request.args.get("year")
    month_param = request.args.get("month")
    type_param = request.args.get("type", "")

    year = int(year_param) if year_param else None
    month = int(month_param) if month_param else None

    data = storage.load_data()
    all_txs = data["transactions"]
    categories = data["categories"]

    filtered = services.filter_transactions(all_txs, year=year, month=month, tx_type=type_param)
    enriched = services.enrich_transactions(filtered, categories)
    months = services.available_months(all_txs)

    return render_template(
        "transactions.html",
        transactions=enriched,
        months=months,
        selected_year=year,
        selected_month=month,
        selected_type=type_param,
    )


@app.route("/transactions/add", methods=["GET", "POST"])
def add_transaction():
    categories = storage.get_categories()

    if request.method == "POST":
        form = request.form
        errors = models.validate_transaction(form, categories)

        if errors:
            return render_template(
                "add_transaction.html",
                categories=categories,
                errors=errors,
                form=form,
            )

        storage.add_transaction(
            tx_type=form["type"],
            amount=form["amount"],
            date=form["date"],
            description=form["description"],
            category_id=form["category_id"],
        )
        flash("Transaction added successfully.", "success")
        return redirect(url_for("transactions"))

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template(
        "add_transaction.html",
        categories=categories,
        errors={},
        form={"date": today, "type": "expense"},
    )


@app.route("/transactions/delete/<transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    deleted = storage.delete_transaction(transaction_id)
    if deleted:
        flash("Transaction deleted.", "success")
    else:
        flash("Transaction not found.", "error")
    return redirect(url_for("transactions"))


@app.route("/transactions/export")
def export_transactions():
    year_param = request.args.get("year")
    month_param = request.args.get("month")
    type_param = request.args.get("type", "")

    try:
        year = int(year_param) if year_param else None
    except ValueError:
        year = None
    try:
        month = int(month_param) if month_param else None
    except ValueError:
        month = None

    data = storage.load_data()
    all_txs = data["transactions"]
    categories = data["categories"]

    filtered = services.filter_transactions(all_txs, year=year, month=month, tx_type=type_param)
    enriched = services.enrich_transactions(filtered, categories)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Description", "Category", "Type", "Amount"])
    for tx in enriched:
        writer.writerow([
            tx["date"],
            tx["description"],
            tx["category_name"],
            tx["type"],
            f"{tx['amount']:.2f}",
        ])

    filename = "transactions"
    if year and month:
        filename += f"_{year}-{month:02d}"
    elif year:
        filename += f"_{year}"
    if type_param in ("income", "expense"):
        filename += f"_{type_param}"
    filename += ".csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@app.route("/categories", methods=["GET", "POST"])
def categories():
    all_cats = storage.get_categories()
    errors = {}
    form = {}

    if request.method == "POST":
        form = request.form
        errors = models.validate_category(form, all_cats)

        if not errors:
            color = form.get("color", "#6b7280").strip() or "#6b7280"
            storage.add_category(form["name"], color)
            flash("Category added.", "success")
            return redirect(url_for("categories"))

    # Count usage per category
    transactions = storage.get_transactions()
    usage = {}
    for tx in transactions:
        usage[tx["category_id"]] = usage.get(tx["category_id"], 0) + 1

    return render_template(
        "categories.html",
        categories=all_cats,
        usage=usage,
        errors=errors,
        form=form,
    )


@app.route("/categories/delete/<category_id>", methods=["POST"])
def delete_category(category_id):
    success, error_msg = storage.delete_category(category_id)
    if success:
        flash("Category deleted.", "success")
    else:
        flash(error_msg, "error")
    return redirect(url_for("categories"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
