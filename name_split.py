from itertools import permutations

name = "THUZAR THET HTAR"
words = name.split()

all_combinations = list(permutations(words))

for combo in all_combinations:
    print(' '.join(combo))