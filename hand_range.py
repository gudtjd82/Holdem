# 포지션 목록
positions = ["EP", "MP", "LP", "BTN", "SB", "BB"]

# 카드 목록 (숫자와 모양)
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
rank_order = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14
}

suits = ["♠", "♥", "♦", "♣"]

# 기본 핸드레인지 (점진적으로 상속받아 확장)
avg_range = {
    "EP": {
        "suited": [("A", "K"), ("A", "Q")],
        "offsuit": [("A", "A"), ("K", "K"), ("Q", "Q"), ("J", "J"), ("A", "K")]
    }
}
# EP 핸드를 포함하여 MP, LP, BTN, SB, BB 포지션에 추가
avg_range["MP"] = {
    "suited": avg_range["EP"]["suited"] + [("A", "J"), ("A", "T"), ("A", "9"), ("K", "Q"), ("Q", "J")],
    "offsuit": avg_range["EP"]["offsuit"] + [("A", "Q"), ("A", "J"), ("T", "T"), ("9", "9"), ("8", "8"), ("7", "7")]
}
avg_range["LP"] = {
    "suited": avg_range["MP"]["suited"] + [("A", "8"), ("A", "7"), ("A", "6"), ("K", "J"), ("K", "T"), ("K", "9"), ("Q", "T"), ("J", "T")],
    "offsuit": avg_range["MP"]["offsuit"] + [("A", "T"), ("A", "9"), ("A", "8"), ("K", "Q"), ("K", "J"), ("K", "T"), ("Q", "J"), ("6", "6"), ("5", "5"), ("4", "4"), ("3", "3"), ("2", "2")]
}
avg_range["BTN"] = {
    "suited": avg_range["LP"]["suited"] + [("A", "5"), ("A", "4"), ("A", "3"), ("A", "2"), ("K", "8"), ("K", "7"), ("Q", "9"), ("J", "9"), ("T", "9"), ("T", "8"), ("9", "8"), ("8", "7"), ("7", "6")],
    "offsuit": avg_range["LP"]["offsuit"] + [("A", "7"), ("A", "6"), ("A", "5"), ("A", "4"), ("A", "3"), ("A", "2"), ("Q", "T"), ("J", "T")]
}
avg_range["SB"] = {
    "suited": avg_range["BTN"]["suited"] + [("Q", "8"), ("J", "8"), ("9", "7"), ("8", "6"), ("7", "5"), ("6", "5"), ("5", "4")],
    "offsuit": avg_range["BTN"]["offsuit"] + [("Q", "9"), ("T", "9"), ("9", "8")]
}
avg_range["BB"] = {
    "suited": avg_range["SB"]["suited"],
    "offsuit": avg_range["SB"]["offsuit"]
}


# 숏 핸드 핸드레인지
short_hand_range = {
    "EP": {
        "suited": [("A", "K"), ("A", "Q"), ("A", "J"), ("A", "T"), ("K", "Q"), ("K", "J"), ("Q", "J")], 
        "offsuit": [("A", "A"), ("K", "K"), ("Q", "Q"), ("J", "J"), ("T", "T"), ("9", "9"), ("8", "8"), ("7", "7"), ("A", "K"), ("A", "Q"), ("A", "J")]
    }
}
# EP 핸드를 포함하여 MP, LP, BTN, SB, BB 포지션에 추가
short_hand_range["MP"] = {
    "suited": short_hand_range["EP"]["suited"] + [("K", "T"), ("Q", "T"), ("J", "T"), ("A", "9"), ("A", "8"), ("A", "7"), ("A", "6")],
    "offsuit": short_hand_range["EP"]["offsuit"] + [("A", "T"), ("A", "9"), ("A", "8"), ("A", "7"), ("6", "6"), ("5", "5"), ("4", "4")]
}
short_hand_range["LP"] = {
    "suited": short_hand_range["MP"]["suited"] + [("A", "5"), ("A", "4"), ("A", "3"), ("A", "2"), ("K", "9"), ("K", "8"), ("Q", "9")],
    "offsuit": short_hand_range["MP"]["offsuit"] + [("A", "6"), ("A", "5"), ("A", "4"), ("A", "3"), ("A", "2"), ("K", "Q"), ("K", "J"), ("K", "T"), ("Q", "J"), ("3", "3"), ("2", "2")]
}
short_hand_range["BTN"] = {
    "suited": short_hand_range["LP"]["suited"] + [("K", "7"), ("K", "6"), ("Q", "8"), ("Q", "7"), ("J", "9"), ("J", "8"), ("J", "7"), ("T", "9"), ("T", "8"), ("T", "7"), ("9", "8"), ("9", "7"), ("8", "7"), ("7", "6"), ("6", "5")],
    "offsuit": short_hand_range["LP"]["offsuit"] + [("K", "9"), ("K", "8"), ("Q", "T"), ("Q", "9"), ("J", "T"), ("J", "9"), ("T", "9")]
}
short_hand_range["SB"] = {
    "suited": short_hand_range["BTN"]["suited"] + [("K", "5"), ("K", "4"), ("9", "6"), ("8", "6"), ("8", "5"), ("7", "5"), ("6", "4"), ("5", "4")],
    "offsuit": short_hand_range["BTN"]["offsuit"] + [("K", "7"), ("K", "6"), ("Q", "8"), ("Q", "7"), ("J", "8"), ("T", "8"), ("9", "8"), ("9", "7"), ("8", "7"), ("7", "6")]
}
short_hand_range["BB"] = {
    "suited": short_hand_range["SB"]["suited"],
    "offsuit": short_hand_range["SB"]["offsuit"]
}