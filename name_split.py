from itertools import permutations

name = "KAPILA DHRUV"
words = name.split()

all_combinations = list(permutations(words))

for combo in all_combinations:
    print(' '.join(combo))