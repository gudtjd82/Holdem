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
    # 게임 ID 생성 또는 가져오기
    game_id = request.args.get('game_id')
    if not game_id:
        game_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return render_template('lobby.html', game_id=game_id)
    else:
        session['game_id'] = game_id
        username = request.args.get('username')
        if username:
            session['username'] = username
            return render_template('game.html', game_id=game_id)
        else:
            return render_template('lobby.html', game_id=game_id)

@socketio.on('join')
def on_join(data):
    username = data['username']
    game_id = data['game_id']
    session['username'] = username
    join_room(game_id)

    if game_id not in games:
        # 새로운 게임 초기화
        games[game_id] = {
            'players': [],
            'deck': create_deck(),
            'community_cards': [],
            'current_bets': {},
            'pot': 0
        }
        random.shuffle(games[game_id]['deck'])

    game = games[game_id]
    # 이미 참여한 플레이어인지 확인
    if username not in [p['username'] for p in game['players']]:
        game['players'].append({
            'username': username,
            'hand': deal_cards(game['deck'], 2),
            'chips': 1000,
            'current_bet': 0,
            'has_folded': False
        })

    emit('player_joined', {'username': username}, room=game_id)

    if len(game['players']) == 2:
        # 두 명의 플레이어가 참여하면 게임 시작
        emit('start_game', {'players': [p['username'] for p in game['players']]}, room=game_id)
        # 초기 핸드 전송
        for player in game['players']:
            sid = request.sid if player['username'] == username else None
            emit('deal_hand', {'hand': player['hand']}, room=sid)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port)
    socketio.run(app, debug=True)