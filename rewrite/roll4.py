import random

def roll(): return random.randint(1, 6) + random.randint(1, 6)

def simulate(n):
    d = {}
    for i in range(2, 13): d[i] = 0
    for _ in range(n): d[roll()] += 1
    return d

def calc(f, t): return {k: v / t for k, v in f.items()}

def display(p):
    print("Sum | Probability")
    print("-----------------")
    for k, v in sorted(p.items()): print(f" {k}  | {v:.2%}")

if __name__ == "__main__":
    x = 10000
    f = simulate(x)
    display(calc(f, x))
