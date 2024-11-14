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
    if request.method == "POST":
        range_sel = request.form.get("range")
        hand_range = avg_range if range_sel == "1" else short_hand_range

        position, hand = deal_preflop()
        action = request.form.get("action")

        if action in ["F", "R"]:
            correct, correct_action = check_action(hand_range, position, hand, action)
            message = "Correct!" if correct else f"Incorrect. The correct action was {correct_action}."
        else:
            message = "Invalid action. Please enter 'F' or 'R'."

        return render_template_string(TEMPLATE, position=position, hand=hand, message=message, accuracy=None)

    return render_template_string(TEMPLATE, position=None, hand=None, message=None, accuracy=None)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hold'em Preflop</title>
</head>
<body>
    <h1>Texas Hold'em Preflop Trainer</h1>
    <form method="POST">
        <label>Select the range:</label><br>
        <input type="radio" name="range" value="1" required> Average range<br>
        <input type="radio" name="range" value="2" required> Short-hand range<br><br>

        <label>Enter your action (F for Fold / R for Raise):</label><br>
        <input type="text" name="action" required><br><br>

        <button type="submit">Submit</button>
    </form>

    {% if position and hand %}
        <h2>Position: {{ position }}</h2>
        <h2>Hand: {{ hand[0] }}, {{ hand[1] }}</h2>
    {% endif %}

    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
