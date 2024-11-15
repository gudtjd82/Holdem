from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import string
import os
from card import *

app = Flask(__name__)
# app.secret_key = 'tjdgus02@@'  # 보안을 위해 실제 비밀 키로 변경하세요.
app.secret_key = os.environ.get('SECRET_KEY', 'tjdgus02@@')
socketio = SocketIO(app, manage_session=True)

# 게임 상태 관리
games = {}

# 카드 덱과 무늬
# SUITS = ['♠', '♥', '♦', '♣']
# RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
#          'J', 'Q', 'K', 'A']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    # 테이블 ID 생성 또는 가져오기
    table_id = request.args.get('table_id')
    starting_chips = request.args.get('starting_chips', type=int)

    if not table_id:
        # 새로운 테이블 생성
        table_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if starting_chips is None:
            starting_chips = 1000  # 기본 시작 칩 액수 설정
        session['starting_chips'] = starting_chips
        return render_template('lobby.html', table_id=table_id)
    else:
        # 기존 테이블에 참여
        session['table_id'] = table_id
        username = request.args.get('username')
        if username:
            session['username'] = username
            return render_template('game.html', table_id=table_id)
        elif 'username' in session:
            # 세션에 사용자 이름이 있으면 게임으로 이동
            return render_template('game.html', table_id=table_id)
        else:
            # 사용자 이름이 없으면 로비로 이동
            return render_template('lobby.html', table_id=table_id)

@socketio.on('join')
@socketio.on('join')
def on_join(data):
    username = data['username']
    table_id = data['table_id']
    session['username'] = username
    session['table_id'] = table_id
    join_room(table_id)

    if table_id not in games:
        # 새로운 테이블 초기화
        starting_chips = session.get('starting_chips', 1000)  # 기본값 1000
        games[table_id] = {
            'players': [],
            'deck': create_deck(),
            'community_cards': [],
            'current_bets': {},
            'pot': 0,
            'starting_chips': starting_chips
        }
        random.shuffle(games[table_id]['deck'])

    game = games[table_id]

    # 플레이어가 이미 게임에 있는지 확인
    player = next((p for p in game['players'] if p['username'] == username), None)
    if player:
        # 플레이어의 sid 업데이트
        player['sid'] = request.sid
    else:
        # 새로운 플레이어 추가
        player = {
            'username': username,
            'hand': deal_cards(game['deck'], 2),
            'chips': game['starting_chips'],  # 시작 칩 액수 사용
            'current_bet': 0,
            'has_folded': False,
            'sid': request.sid  # Socket.IO 세션 ID 저장
        }
        game['players'].append(player)

    emit('player_joined', {'username': username}, room=table_id)

    # 플레이어에게 자신의 핸드 전송
    emit('deal_hand', {'hand': player['hand']}, room=player['sid'])

    if len(game['players']) == 2:
        # 두 명의 플레이어가 참여하면 게임 시작
        emit('start_game', {'players': [p['username'] for p in game['players']]}, room=table_id)

@socketio.on('place_bet')
def on_place_bet(data):
    game_id = session['game_id']
    username = session['username']
    bet_amount = int(data['bet_amount'])

    game = games[game_id]
    player = next(p for p in game['players'] if p['username'] == username)
    player['chips'] -= bet_amount
    player['current_bet'] += bet_amount
    game['pot'] += bet_amount

    emit('bet_placed', {'username': username, 'bet_amount': bet_amount, 'chips': player['chips'], 'pot': game['pot']}, room=game_id)

    # 간단한 베팅 라운드 로직
    if all(p['current_bet'] > 0 for p in game['players']):
        # 다음 단계로 진행 (예: 플랍, 턴, 리버)
        if len(game['community_cards']) < 5:
            # 커뮤니티 카드 배분
            if len(game['community_cards']) == 0:
                # 플랍
                game['community_cards'].extend(deal_cards(game['deck'], 3))
            else:
                # 턴 또는 리버
                game['community_cards'].extend(deal_cards(game['deck'], 1))
            # 현재 베팅 초기화
            for p in game['players']:
                p['current_bet'] = 0
            emit('update_community', {'community_cards': game['community_cards']}, room=game_id)
        else:
            # 쇼다운
            active_players = [p for p in game['players'] if not p['has_folded']]
            if active_players:
                # 각 플레이어의 핸드를 평가
                player_hands = {}
                for p in active_players:
                    total_cards = p['hand'] + game['community_cards']
                    best_hand = get_best_hand(total_cards)
                    evaluated_hand = evaluate_hand(best_hand)
                    player_hands[p['username']] = evaluated_hand

                # 승자 결정
                winner = max(player_hands.items(), key=lambda x: x[1])
                winner_name = winner[0]
                winner_player = next(p for p in active_players if p['username'] == winner_name)
                winner_player['chips'] += game['pot']

                emit('showdown', {'winner': winner_name, 'pot': game['pot']}, room=game_id)
            else:
                emit('showdown', {'winner': None, 'pot': game['pot']}, room=game_id)
            # 게임 초기화
            games.pop(game_id)

@socketio.on('fold')
def on_fold():
    game_id = session['game_id']
    username = session['username']

    game = games[game_id]
    player = next(p for p in game['players'] if p['username'] == username)
    player['has_folded'] = True

    emit('player_folded', {'username': username}, room=game_id)

    # 남은 플레이어가 한 명인지 확인
    active_players = [p for p in game['players'] if not p['has_folded']]
    if len(active_players) == 1:
        winner = active_players[0]
        winner['chips'] += game['pot']
        emit('showdown', {'winner': winner['username'], 'pot': game['pot']}, room=game_id)
        # 게임 초기화
        games.pop(game_id)

@socketio.on('request_chips')
def on_request_chips():
    username = session['username']
    table_id = session['table_id']
    game = games.get(table_id)
    if game:
        player = next((p for p in game['players'] if p['username'] == username), None)
        if player:
            emit('update_chips', {'username': username, 'chips': player['chips']}, room=player['sid'])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port)
    socketio.run(app, debug=True)