"""Web page that runs one simulated coffee-shop morning on every load."""

import base64
import io

import matplotlib

matplotlib.use("Agg")  # render to images; no display needed on a server
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template_string

from coffee import OPEN_MINUTES, simulate_with_arrivals

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coffee Shop Morning</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; }
    .stats { display: flex; gap: 2rem; margin: 1rem 0; }
    .stat b { display: block; font-size: 2rem; }
    img { max-width: 100%; height: auto; }
  </style>
</head>
<body>
  <h1>One morning at the coffee shop</h1>
  <p>7:00&ndash;11:00, one barista. Reload the page to simulate another morning.</p>
  <div class="stats">
    <div class="stat"><b>{{ served }}</b>customers served</div>
    <div class="stat"><b>{{ avg_wait }}</b>average wait (minutes)</div>
  </div>
  {% if chart %}
    <img src="data:image/png;base64,{{ chart }}" alt="Each customer's wait by arrival time">
  {% endif %}
</body>
</html>
"""


def wait_chart(arrivals, waits):
    """Plot each customer's wait against their arrival time; return a base64 PNG."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(arrivals, waits, marker="o", markersize=3, linewidth=1)
    hours = np.arange(0, OPEN_MINUTES + 1, 60)
    ax.set_xticks(hours, [f"{7 + h // 60}:00" for h in hours])
    ax.set_xlim(0, OPEN_MINUTES)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Arrival time")
    ax.set_ylabel("Wait (minutes)")
    ax.set_title("Each customer's wait through the morning")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.route("/")
def index():
    rng = np.random.default_rng()
    arrivals, waits = simulate_with_arrivals(rng)
    return render_template_string(
        PAGE,
        served=waits.size,
        avg_wait=f"{waits.mean():.2f}" if waits.size else "n/a",
        chart=wait_chart(arrivals, waits) if waits.size else None,
    )


if __name__ == "__main__":
    app.run(debug=True)
