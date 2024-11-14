from flask import Flask, request, render_template_string, send_from_directory
import random
import os
from hand_range import *

app = Flask(__name__)

# 정적 디렉토리 설정
RANGE_IMG_DIR = os.path.join(os.path.dirname(__file__), 'range_img')

@app.route("/range_image/<filename>")
def range_image(filename):
    # range_img 디렉토리에서 파일 제공
    return send_from_directory(RANGE_IMG_DIR, filename)

# Initialize counters for tracking action accuracy
total_attempts = 0
correct_attempts = 0

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
    global total_attempts, correct_attempts
    message = None
    range_sel = "1"
    range_name = "Average Range"

    if request.method == "POST":
        if request.form.get("reset") == "true":
            # Reset accuracy counters
            total_attempts = 0
            correct_attempts = 0
            position, hand = deal_preflop()
            accuracy = "0/0 correct (0.00%)"
            return render_template_string(TEMPLATE, position=position, hand=hand, message=None, range_sel=request.form.get("range"), range_name=range_name, accuracy=accuracy)

        range_sel = request.form.get("range")
        hand_range = avg_range if range_sel == "1" else short_hand_range
        range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"
        position = request.form.get("position")
        hand = eval(request.form.get("hand"))  # Convert back to tuple
        action = request.form.get("action")

        correct, correct_action = check_action(hand_range, position, hand, action)
        total_attempts += 1
        if correct:
            correct_attempts += 1
        message = "Previous Hand: " + ("Correct!" if correct else f"Incorrect. The correct action was {correct_action}.")

        # Deal new hand automatically
        position, hand = deal_preflop()
    else:
        range_sel = request.args.get("range", "1")
        hand_range = avg_range if range_sel == "1" else short_hand_range
        range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"
        position, hand = deal_preflop()

    # Calculate accuracy
    accuracy = f"{correct_attempts}/{total_attempts} correct ({(correct_attempts / total_attempts * 100):.2f}%)" if total_attempts > 0 else "0/0 correct (0.00%)"

    return render_template_string(TEMPLATE, position=position, hand=hand, message=message, range_sel=range_sel, range_name=range_name, accuracy=accuracy)

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
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px;
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
        .reset {
            background-color: transparent;
            color: #555;
            font-size: 14px;
            padding: 5px;
            border: none;
            cursor: pointer;
        }
        .reset:hover {
            color: #000;
        }
        .accuracy {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .small-link {
            font-size: 10px;
            margin-top: -5px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Texas Hold'em Trainer</h1>

        <div class="button-container">
            <div>
                <form method="GET">
                    <button type="submit" name="range" value="1" class="button">Average Range</button>
                </form>
                <p class="small-link"><a href="/range_image/avg_range.jpeg" target="_blank">View Average Range</a></p>
            </div>
            <div>
                <form method="GET">
                    <button type="submit" name="range" value="2" class="button">Short-Hand Range</button>
                </form>
                <p class="small-link"><a href="/range_image/SH_range.jpeg" target="_blank">View Short-Hand Range</a></p>
            </div>
        </div>

        <div class="accuracy">
            <p>Accuracy: <strong>{{ accuracy }}</strong></p>
            <form method="POST" style="display: inline; margin-left: 10px;">
                <input type="hidden" name="reset" value="true">
                <button type="submit" class="reset">&#x21bb;</button>
            </form>
        </div>

        {% if message %}
            <p><strong>{{ message }}</strong></p>
        {% endif %}

        {% if position and hand %}
            <h2>Position: {{ position }}</h2>
            <h2>Hand: {{ hand[0] }}, {{ hand[1] }}</h2>
        {% endif %}

        <form method="POST">
            <input type="hidden" name="range" value="{{ range_sel }}">
            <input type="hidden" name="position" value="{{ position }}">
            <input type="hidden" name="hand" value="{{ hand }}">
            <button type="submit" name="action" value="F" class="button fold">Fold</button>
            <button type="submit" name="action" value="R" class="button raise">Raise</button>
        </form>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)

