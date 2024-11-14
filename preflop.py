import random
from hand_range import *

# 랜덤 포지션과 핸드를 생성하는 함수
def deal_preflop():
    position = random.choice(positions)
    card1 = random.choice(ranks) + random.choice(suits)
    card2 = random.choice(ranks) + random.choice(suits)
    
    # Ensure that the two cards are not the same
    while card1 == card2:
        card2 = random.choice(ranks) + random.choice(suits)

    print("============================")
    print(f"Position: {position}")
    print(f"Hand: {card1}, {card2}")
    return position, (card1, card2)

# 액션 확인 함수
def check_action(hand_range, position, hand, action):
    card1, card2 = hand
    # 수딧 여부 확인 (문양이 같으면 suited)
    hand_type = "suited" if card1[-1] == card2[-1] else "offsuit"
    
    # 숫자를 기준으로 정렬
    rank1 = rank_order[card1[:-1]]  # 숫자만 추출 후 순위 매핑
    rank2 = rank_order[card2[:-1]]  # 숫자만 추출 후 순위 매핑
    hand_ranks = tuple(sorted([rank1, rank2], reverse=True))  # 높은 카드가 앞에 오도록 정렬
    
    # 숫자를 다시 문자열로 변환
    hand_ranks = tuple(sorted([card1[:-1], card2[:-1]], key=lambda r: rank_order[r], reverse=True))
    
    # 핸드레인지에서 확인
    if hand_ranks in hand_range[position][hand_type]:
        correct_action = "R"
    else:
        correct_action = "F"
    
    # 사용자 액션 검증
    if action == correct_action:
        print("Correct!")
        return True
    else:
        print(f"Incorrect. The correct action was {correct_action}.")
        return False

# 메인 실행 루프
def main():
    range_sel = input("Select the range \n 1. Average range // 2. Short-hand range\n")
    if range_sel == "1":
        hand_range = avg_range
    elif range_sel == "2":
        hand_range = short_hand_range
    else:
        exit("Error: Invalid selection!")

    total_attempts = 0
    correct_attempts = 0
        
    print("Press 'x' to stop the program.")
    while True:
        position, hand = deal_preflop()
        action = input("Enter your action (F for Fold / R for Raise / x to exit): \n").strip().capitalize()
        if action in ["F", "R"]:
            total_attempts +=1
            if check_action(hand_range, position, hand, action):
                correct_attempts +=1
        elif action == "X":
            print("Process stopped by user.")
            if total_attempts > 0:
                accuracy = (correct_attempts / total_attempts) * 100
                print("============================")
                print(f"Your accuracy: {accuracy:.2f}% ({correct_attempts}/{total_attempts} correct)")
            else:
                print("No attempts were made.")
            break
        else:
            print("Invalid action. Please enter 'F', 'R', or 'x'.")

if __name__ == "__main__":
    main()

    # position = "SB"
    # hand = ("T♦", "9♠")
    # action = "R"

    # check_action(avg_range, position, hand, action)
    # check_action(short_hand_range, position, hand, action)