from flask import Flask, render_template, request
import json
import socket
import webbrowser
import threading
import time
import os

app = Flask(__name__, template_folder="templates")

questions = { ... }  # Innehållet är förkortat här för utrymme

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart_data = {}
    top_match = None

    if request.method == "POST":
        scores = {"strategy": 0, "consulting": 0, "assurance": 0, "tax": 0}
        for i in range(1, 11):
            response = request.form.get(f"q{i}")
            if response:
                parts = response.split(',')
                for part in parts:
                    key, val = part.split(':')
                    scores[key] += int(val)

        total = sum(scores.values())
        if total > 0:
            percentages = {k: round(v / total * 100) for k, v in scores.items()}
            sorted_matches = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            result = " ".join([f"{k}:{v}" for k, v in sorted_matches])
            chart_data = json.dumps(percentages)
            top_match = (
                'Strategy & Transactions' if sorted_matches[0][0] == 'strategy' else
                'Tax & Law' if sorted_matches[0][0] == 'tax' else
                sorted_matches[0][0].capitalize()
            )

    return render_template("index.html", result=result, questions=questions, chart_data=chart_data, top_match=top_match)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
