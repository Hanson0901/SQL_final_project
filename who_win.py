def get_final_winner(score_str):
    scores = list(map(int, score_str.strip().split()))
    a_win, b_win = 0, 0
    for i in range(0, len(scores), 2):
        a, b = scores[i], scores[i+1]
        if a > b:
            a_win += 1
        elif b > a:
            b_win += 1
        # 判斷是否已經有人兩勝
        if a_win == 2:
            return "A"
        if b_win == 2:
            return "B"
   

score = "21 17 13 21"
print(get_final_winner(score))  # 輸出: B