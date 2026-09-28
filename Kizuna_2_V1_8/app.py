import os
import sqlite3
from flask import Flask, abort, render_template, url_for

from content import PILOT_DIRECTORY_PAGES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "kizuna.db")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_asset_path(value):
    """Convert legacy DB paths into URLs usable by Flask's static folder."""
    if not value or str(value).strip().lower() in {"none", "null"}:
        return None
    value = str(value).strip().replace("\\", "/")
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("/static/"):
        return value
    if value.startswith("static/"):
        return "/" + value
    return url_for("static", filename=value.lstrip("/"))


def normalize_record(row):
    item = dict(row)
    for key in ("logo", "foto1", "foto2", "foto3", "foto4"):
        item[key] = normalize_asset_path(item.get(key))
    # NULL and empty strings both mean "not available" to the presentation layer.
    for key in ("Whatsapp", "Instagram", "Facebook", "X", "Webpage", "Email"):
        value = item.get(key)
        if value is not None:
            value = str(value).strip()
        item[key] = value or None
    return item


def get_directory_records(activity):
    conn = get_db()
    try:
        # activity comes only from the controlled PILOT_DIRECTORY_PAGES configuration.
        rows = conn.execute(
            f"SELECT * FROM directorio WHERE {activity} = 1"
        ).fetchall()
        records = [normalize_record(row) for row in rows]
        return sorted(records, key=lambda item: (str(item.get("Nombre") or "").casefold(), item.get("ID") or 0))
    finally:
        conn.close()


def group_records(records):
    """Put every Caracas organization in the first group, then group the rest by state."""
    caracas = []
    states = {}

    for item in records:
        city = str(item.get("Ciudad") or "").strip()
        state = str(item.get("Estado") or "").strip()

        # Caracas is a special first group regardless of whether its Estado is
        # Distrito Capital or Miranda. It must not appear again under Miranda.
        if city.casefold() == "caracas":
            caracas.append(item)
            continue

        state_name = state or "Otros Estados"
        states.setdefault(state_name, []).append(item)

    caracas.sort(key=lambda item: (str(item.get("Nombre") or "").casefold(), item.get("ID") or 0))
    ordered_states = {}
    for state_name in sorted(states, key=str.casefold):
        ordered_states[state_name] = sorted(
            states[state_name],
            key=lambda item: (str(item.get("Nombre") or "").casefold(), item.get("ID") or 0),
        )

    return caracas, ordered_states


@app.route("/")
def index():
    return render_template("pages/home.html")


@app.route("/cultura/<slug>")
def culture_detail(slug):
    page = PILOT_DIRECTORY_PAGES.get(slug)
    if not page:
        abort(404)
    records = get_directory_records(page["activity"])
    caracas, states = group_records(records)
    return render_template(
        "pages/detail.html",
        page=page,
        caracas=caracas,
        states=states,
    )


@app.errorhandler(404)
def not_found(_error):
    return render_template("pages/404.html"), 404


if __name__ == "__main__":
    # Debug/reloader is intentionally disabled for the local prototype to avoid
    # duplicate Flask processes and confusing port-5000 behavior on Windows.
    app.run(debug=False, host="127.0.0.1", port=5000)
