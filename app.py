from flask import Flask, request, render_template_string, send_from_directory, session
import random
import os
from hand_range import *

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 비밀 키를 설정합니다.

# 정적 디렉토리 설정
RANGE_IMG_DIR = os.path.join(os.path.dirname(__file__), 'range_img')

@app.route("/range_image/<filename>")
def range_image(filename):
    # range_img 디렉토리에서 파일 제공
    return send_from_directory(RANGE_IMG_DIR, filename)

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
    # 세션에서 카운터와 변수를 초기화
    if 'total_attempts' not in session:
        session['total_attempts'] = 0
    if 'correct_attempts' not in session:
        session['correct_attempts'] = 0
    if 'action_taken' not in session:
        session['action_taken'] = False

    message = None
    range_sel = session.get('range_sel', '1')
    range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"

    if request.method == "POST":
        if request.form.get("reset") == "true":
            # 카운터 리셋
            session['total_attempts'] = 0
            session['correct_attempts'] = 0
            session['action_taken'] = False
            # 새로운 핸드 배분
            position, hand = deal_preflop()
            session['current_position'] = position
            session['current_hand'] = hand
            session['previous_position'] = None
            session['previous_hand'] = None
            message = "Counters have been reset."
        elif request.form.get("action") == "previous":
            # 이전 핸드로 돌아가기
            if session.get('previous_position') and session.get('previous_hand'):
                session['current_position'] = session['previous_position']
                session['current_hand'] = session['previous_hand']
                session['action_taken'] = False
                message = "Returned to previous hand."
            else:
                message = "No previous hand available."
        else:
            # 액션 처리
            range_sel = request.form.get("range", session.get('range_sel', '1'))
            session['range_sel'] = range_sel
            hand_range = avg_range if range_sel == "1" else short_hand_range
            range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"

            position = session.get('current_position')
            hand = session.get('current_hand')
            action = request.form.get("action") or request.form.get("key_action")

            if not session['action_taken']:
                # 액션 처리
                correct, correct_action = check_action(hand_range, position, hand, action)
                session['total_attempts'] += 1
                if correct:
                    session['correct_attempts'] += 1
                message = "(Previous Hand: " + ("Correct!)" if correct else f"Incorrect. The correct action was {correct_action}.)")
                session['action_taken'] = True
            else:
                # 이미 액션을 선택한 경우
                message = "Action already taken on this hand."

            # 현재 핸드를 이전 핸드로 저장
            session['previous_position'] = session['current_position']
            session['previous_hand'] = session['current_hand']

            # 새로운 핸드 배분
            position, hand = deal_preflop()
            session['current_position'] = position
            session['current_hand'] = hand
            session['action_taken'] = False

    else:
        # GET 요청 처리
        if request.args.get('range'):
            range_sel = request.args.get('range')
            session['range_sel'] = range_sel
            range_name = "Average Range" if range_sel == "1" else "Short-Hand Range"
            # 새로운 핸드 배분
            position, hand = deal_preflop()
            session['current_position'] = position
            session['current_hand'] = hand
            session['action_taken'] = False
        else:
            # 기존 핸드 사용 또는 새로운 핸드 배분
            position = session.get('current_position')
            hand = session.get('current_hand')
            if not position or not hand:
                position, hand = deal_preflop()
                session['current_position'] = position
                session['current_hand'] = hand
                session['action_taken'] = False

    # 정확도 계산
    total_attempts = session['total_attempts']
    correct_attempts = session['correct_attempts']
    accuracy = f"{correct_attempts}/{total_attempts} correct ({(correct_attempts / total_attempts * 100):.2f}%)" if total_attempts > 0 else "0/0 correct (0.00%)"

    return render_template_string(TEMPLATE, position=session['current_position'], hand=session['current_hand'], message=message, range_sel=range_sel, range_name=range_name, accuracy=accuracy)

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
            gap: 10px; /* 간격을 조절합니다 */
            margin-bottom: 20px;
        }
        .previous {
            background-color: #007BFF;
            color: white;
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
            <!-- 이름을 변경하여 충돌을 방지합니다 -->
            <input type="hidden" name="key_action" id="key-action-input">
            <div class="action-buttons">
                <button type="submit" name="action" value="previous" class="button previous">Previous Hand</button>
                <button type="submit" name="action" value="F" class="button fold">Fold</button>
                <button type="submit" name="action" value="R" class="button raise">Raise</button>
            </div>
        </form>
    </div>

    <script>
    document.addEventListener('keydown', function(event) {
        if (event.key === 'r' || event.key === 'R') {
            document.getElementById('key-action-input').value = 'R';
            document.getElementById('action-form').submit();
        } else if (event.key === 'f' || event.key === 'F') {
            document.getElementById('key-action-input').value = 'F';
            document.getElementById('action-form').submit();
        } else if (event.key === 'e' || event.key === 'E') {
            document.getElementById('key-action-input').value = 'previous';
            document.getElementById('action-form').submit();
        }
    });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)