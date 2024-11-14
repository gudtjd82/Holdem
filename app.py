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

# 정확도 추적을 위한 카운터 초기화
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
            # 정확도 카운터 초기화
            total_attempts = 0
            correct_attempts = 0
            position, hand = deal_preflop()
            accuracy = "0/0 correct (0.00%)"
            return render_template_string(TEMPLATE, position=position, hand=hand, message=None, range_sel=request.form.get("range"), range_name=range_name, accuracy=accuracy)

        range_sel = request.form.get("range")
        hand_range = avg_range if range_sel == "1" else short_hand_range
        range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"
        position = request.form.get("position")
        hand = eval(request.form.get("hand"))  # 튜플로 다시 변환
        action = request.form.get("action")

        correct, correct_action = check_action(hand_range, position, hand, action)
        total_attempts += 1
        if correct:
            correct_attempts += 1
        message = "(Previous Hand: " + ("Correct!)" if correct else f"Incorrect. The correct action was {correct_action}.)")

        # 자동으로 새로운 핸드 배분
        position, hand = deal_preflop()
    else:
        range_sel = request.args.get("range", "1")
        hand_range = avg_range if range_sel == "1" else short_hand_range
        range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"
        position, hand = deal_preflop()

    # 정확도 계산
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
            margin: 0;
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .button-container {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }
        .button {
            padding: 10px 15px;
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
            text-align: center;
            margin-bottom: 20px;
        }
        .accuracy-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .message {
            font-size: 12px;
            color: #555;
        }
        .small-link {
            font-size: 10px;
            margin: 0;
            text-align: center;
        }
        .info-box {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            background-color: #fafafa;
        }
        .info-box h2 {
            margin: 5px 0;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
        }
        .range-title {
            text-align: center;
            margin-bottom: 10px;
        }
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 20px; /* 간격을 조절합니다 */
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Texas Hold'em Trainer</h1>

        <div class="range-title">
            <h2>Current Range: {{ range_name }}</h2>
        </div>

        <div class="button-container">
            <div>
                <form method="GET">
                    <button type="submit" name="range" value="1" class="button">Average Range</button>
                </form>
                <p class="small-link">
                    <a href="/range_image/avg_range.jpeg" target="_blank">View Average Range</a>
                </p>
            </div>
            <div>
                <form method="GET">
                    <button type="submit" name="range" value="2" class="button">Short-Hand Range</button>
                </form>
                <p class="small-link">
                    <a href="/range_image/SH_range.jpeg" target="_blank">View Short-Hand Range</a>
                </p>
            </div>
        </div>

        <div class="accuracy">
            <div class="accuracy-row">
                <p>Accuracy: <strong>{{ accuracy }}</strong></p>
                <form method="POST">
                    <input type="hidden" name="reset" value="true">
                    <button type="submit" class="reset">&#x21bb;</button>
                </form>
            </div>
            {% if message %}
                <p class="message">{{ message }}</p>
            {% endif %}
        </div>

        {% if position and hand %}
        <div class="info-box">
            <h2>Position: {{ position }}</h2>
            <h2>Hand: {{ hand[0] }}, {{ hand[1] }}</h2>
        </div>
        {% endif %}

        <form method="POST" id="action-form">
            <input type="hidden" name="range" value="{{ range_sel }}">
            <input type="hidden" name="position" value="{{ position }}">
            <input type="hidden" name="hand" value="{{ hand }}">
            <input type="hidden" name="action" id="action-input">
            <div class="action-buttons">
                <button type="submit" name="action" value="F" class="button fold">Fold</button>
                <button type="submit" name="action" value="R" class="button raise">Raise</button>
            </div>
        </form>
    </div>

    <script>
    document.addEventListener('keydown', function(event) {
        if (event.key === 'r' || event.key === 'R') {
            document.getElementById('action-input').value = 'R';
            document.getElementById('action-form').submit();
        } else if (event.key === 'f' || event.key === 'F') {
            document.getElementById('action-input').value = 'F';
            document.getElementById('action-form').submit();
        }
    });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)