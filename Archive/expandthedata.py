import random

# Input and output
input_file = "training_balanced.txt"
output_file = "training_balanced2.txt"

# Load pairs
pairs = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            wrong, right = line.split()
            pairs.append((wrong, right))

# Common Telugu phonetic confusion patterns (Romanized)
confusions = {
    "ch": ["c", "sh"],
    "sh": ["s", "ch"],
    "dh": ["d"],
    "th": ["t"],
    "ph": ["f"],
    "bh": ["b"],
    "aa": ["a"],
    "ee": ["e", "i"],
    "oo": ["o", "u"],
    "u": ["oo"],
    "i": ["ee"],
    "e": ["ae", "i"],
    "k": ["c"],
    "g": ["gh"],
    "t": ["th"],
    "d": ["dh"],
    "n": ["nn"],
    "m": ["mm"],
    "r": ["rr"],
    "l": ["ll"],
}

def make_typo(word):
    typo = list(word)
    if not typo:
        return word  # skip empty lines

    typo_type = random.choice(["swap", "drop", "double", "vowel_swap"])

    if typo_type == "swap" and len(typo) > 1:
        idx = random.randint(0, len(typo) - 2)
        typo[idx], typo[idx + 1] = typo[idx + 1], typo[idx]

    elif typo_type == "drop" and len(typo) > 1:
        idx = random.randint(0, len(typo) - 1)
        typo.pop(idx)

    elif typo_type == "double":
        idx = random.randint(0, len(typo) - 1)
        typo.insert(idx, typo[idx])

    elif typo_type == "vowel_swap":
        vowels = {"a", "e", "i", "o", "u"}
        for i, ch in enumerate(typo):
            if ch in vowels and random.random() < 0.3:
                typo[i] = random.choice(list(vowels))

    return "".join(typo)


# Step 1: Keep originals
augmented = list(pairs)

# Step 2: Generate 3 typos for each correct word
for wrong, correct in pairs:
    for _ in range(3):
        new_wrong = make_typo(correct)
        if new_wrong != correct:
            augmented.append((new_wrong, correct))

# Step 3: Balance by adding correct→correct pairs
wrong_to_right = [p for p in augmented if p[0] != p[1]]
right_to_right = [p for p in augmented if p[0] == p[1]]

# We want equal amounts of both
needed_balancing = max(0, len(wrong_to_right) - len(right_to_right))
unique_correct_words = list({r for _, r in pairs})

for _ in range(needed_balancing):
    w = random.choice(unique_correct_words)
    augmented.append((w, w))  # same word (correct→correct)

# Step 4: Shuffle and save
random.shuffle(augmented)

with open(output_file, "w", encoding="utf-8") as f:
    for w, c in augmented:
        f.write(f"{w} {c}\n")

print(f"✅ Augmentation + Balancing complete!")
print(f"Original pairs: {len(pairs)}")
print(f"Augmented total: {len(augmented)}")
print(f"Saved to: {output_file}")
