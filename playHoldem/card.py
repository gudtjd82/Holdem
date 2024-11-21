import random

# 포지션 목록
positions = ["EP", "MP", "LP", "BTN", "SB", "BB"]

# 카드 목록 (숫자와 모양)
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
rank_order = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14
}

SUITS = ["♠", "♥", "♦", "♣"]

def create_deck():
    return [rank + suit for suit in SUITS for rank in RANKS]

def deal_cards(deck, num):
    return [deck.pop() for _ in range(num)]

def card_value(card):
    rank = card[:-1]
    return rank_order[rank]

def evaluate_hand(cards):
    # 각 핸드를 평가하여 족보와 랭크를 반환하는 함수
    ranks = sorted([rank_order[card[:-1]] for card in cards], reverse=True)
    suits = [card[-1] for card in cards]
    rank_counts = {rank: ranks.count(rank) for rank in ranks}
    unique_ranks = sorted(set(ranks), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = unique_ranks == list(range(unique_ranks[0], unique_ranks[0]-5, -1))
    # 특수한 스트레이트 처리 (A-2-3-4-5)
    if not is_straight and set([14, 5, 4, 3, 2]).issubset(set(ranks)):
        is_straight = True
        unique_ranks = [5, 4, 3, 2, 1]

    # 족보 결정
    if is_flush and is_straight and unique_ranks[0] == 14:
        rank = 10  # 로열 스트레이트 플러시
    elif is_flush and is_straight:
        rank = 9  # 스트레이트 플러시
    elif 4 in rank_counts.values():
        rank = 8  # 포카드
    elif sorted(rank_counts.values()) == [2, 3]:
        rank = 7  # 풀하우스
    elif is_flush:
        rank = 6  # 플러시
    elif is_straight:
        rank = 5  # 스트레이트
    elif 3 in rank_counts.values():
        rank = 4  # 트리플
    elif list(rank_counts.values()).count(2) == 2:
        rank = 3  # 투페어
    elif 2 in rank_counts.values():
        rank = 2  # 원페어
    else:
        rank = 1  # 하이카드

    return (rank, ranks, rank_counts)

def compare_hands(hand1, hand2):
    # 두 핸드를 비교하여 승자를 결정하는 함수
    rank1, ranks1, counts1 = hand1
    rank2, ranks2, counts2 = hand2

    if rank1 > rank2:
        return 1
    elif rank1 < rank2:
        return -1
    else:
        # 족보가 같을 경우 키커로 비교
        if ranks1 > ranks2:
            return 1
        elif ranks1 < ranks2:
            return -1
        else:
            return 0  # 무승부

def get_best_hand(cards):
    # 7장 중에서 가장 좋은 5장 선택
    from itertools import combinations
    best_hand = None
    best_rank = (0, [])
    for combo in combinations(cards, 5):
        evaluated = evaluate_hand(combo)
        if evaluated[0] > best_rank[0]:
            best_rank = evaluated
            best_hand = combo
        elif evaluated[0] == best_rank[0]:
            if evaluated[1] > best_rank[1]:
                best_rank = evaluated
                best_hand = combo
    return best_hand

def reset_game(game):
    """
    게임 상태를 초기화하지만 플레이어들의 칩 정보는 유지합니다.
    """
    game['deck'] = create_deck()
    random.shuffle(game['deck'])
    game['community_cards'] = []
    game['current_bets'] = {}
    game['pot'] = 0
    for player in game['players']:
        player['hand'] = deal_cards(game['deck'], 2)
        player['current_bet'] = 0
        player['has_folded'] = False