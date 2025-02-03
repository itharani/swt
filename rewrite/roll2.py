import random

def roll_dice():
    return random.randint(1, 6) + random.randint(1, 6)

def simulate_rolls(num_rolls):
    roll_counts = {i: 0 for i in range(2, 13)}
    for _ in range(num_rolls):
        roll_result = roll_dice()
        roll_counts[roll_result] += 1
    return roll_counts

def calculate_probabilities(frequencies, total_rolls):
    return {sum_value: count / total_rolls for sum_value, count in frequencies.items()}

def display_probabilities(probabilities):
    print("Sum | Probability")
    print("-----------------")
    for sum_value, probability in sorted(probabilities.items()):
        print(f" {sum_value}  | {probability:.2%}")

def main():
    num_rolls = 10000
    frequencies = simulate_rolls(num_rolls)
    probabilities = calculate_probabilities(frequencies, num_rolls)
    display_probabilities(probabilities)

if __name__ == "__main__":
    main()