from flask import Flask, render_template, request, jsonify
from datetime import date
from models import compute_value_row

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/value")
def api_value():
    name = request.args.get("player", "")
    year_str = request.args.get("year", "")
    try:
        year = int(year_str) if year_str else date.today().year
    except ValueError:
        year = date.today().year

    row = compute_value_row(name, year)
    if not row:
        return jsonify({"error": "Player/year not found in data."}), 404
    return jsonify(row)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
