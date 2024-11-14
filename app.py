from flask import Flask, request, render_template_string
import random
from hand_range import *

app = Flask(__name__)

def deal_preflop():
    position = random.choice(positions)
    card1 = random.choice(ranks) + random.choice(suits)
    card2 = random.choice(ranks) + random.choice(suits)
    while card1 == card2:
        card2 = random.choice(ranks) + random.choice(suits)
    return position, (card1, card2)

def check_action(hand_range, position, hand, action):
    card1, card2 = hand
    hand_type = "suited" if card1[-1] == card2[-1] else "offsuit"
    hand_ranks = tuple(sorted([card1[:-1], card2[:-1]], key=lambda r: rank_order[r], reverse=True))
    correct_action = "R" if hand_ranks in hand_range[position][hand_type] else "F"
    return action == correct_action, correct_action

@app.route("/", methods=["GET", "POST"])
def main():
    message = None
    position, hand = None, None
    if request.method == "POST":
        range_sel = request.form.get("range")
        hand_range = avg_range if range_sel == "1" else short_hand_range
        position = request.form.get("position")
        hand = eval(request.form.get("hand"))  # Convert back to tuple
        action = request.form.get("action")

        correct, correct_action = check_action(hand_range, position, hand, action)
        message = "Correct!" if correct else f"Incorrect. The correct action was {correct_action}."
    else:
        range_sel = request.args.get("range", "1")
        hand_range = avg_range if range_sel == "1" else short_hand_range
        position, hand = deal_preflop()

    return render_template_string(TEMPLATE, position=position, hand=hand, message=message, range_sel=range_sel)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Texas Hold'em Trainer</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            height: 100vh;
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
        }
        .container {
            text-align: center;
            max-width: 90%;
        }
        .button {
            margin: 10px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .fold {
            background-color: #ff4d4d;
            color: white;
        }
        .raise {
            background-color: #4CAF50;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Texas Hold'em Trainer</h1>
        {% if position and hand %}
            <h2>Position: {{ position }}</h2>
            <h2>Hand: {{ hand[0] }}, {{ hand[1] }}</h2>
        {% endif %}

        {% if message %}
            <p>{{ message }}</p>
        {% endif %}

        <form method="POST">
            <input type="hidden" name="range" value="{{ range_sel }}">
            <input type="hidden" name="position" value="{{ position }}">
            <input type="hidden" name="hand" value="{{ hand }}">
            <button type="submit" name="action" value="F" class="button fold">Fold</button>
            <button type="submit" name="action" value="R" class="button raise">Raise</button>
        </form>

        <form method="GET">
            <button type="submit" name="range" value="1" class="button">Average Range</button>
            <button type="submit" name="range" value="2" class="button">Short-Hand Range</button>
        </form>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
