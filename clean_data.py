#!/usr/bin/env python3
"""Clean Lekha's training data and build proper train/dev/test splits.

What it does
  1. Loads every (typo, correct) pair from the old files.
  2. Applies merges.txt so one Telugu word has ONE canonical spelling.
  3. Fixes label conflicts:
       - an input that is itself a valid word always maps to itself
       - otherwise the majority target wins; ambiguous inputs are dropped
  4. Removes duplicates.
  5. Splits by WORD:  train words / test words (never seen in training).
     A slice of real typos of training words is held out as dev.
  6. Generates realistic synthetic typos for TRAINING words only.

Usage:  python clean_data.py --data . --out clean_data
"""
import argparse
import collections
import math
import os
import random

DEFAULT_FILES = ["training.txt", "training_balanced.txt",
                 "training_balanced2.txt", "userData.txt"]
VOWELS = set("aeiou")


def load_pairs(data_dir, files):
    pairs = []
    for name in files:
        path = os.path.join(data_dir, name)
        if not os.path.exists(path):
            print(f"  (skipping missing file {name})")
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) == 2:
                    pairs.append((parts[0].lower(), parts[1].lower()))
    return pairs


def load_merges(path):
    merges = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                parts = line.split()
                if len(parts) == 2:
                    merges[parts[0]] = parts[1]
    return merges


def resolve(pairs, merges, majority):
    """Return {input: target} with conflicts removed, plus report lines."""
    report = []
    counts = collections.defaultdict(collections.Counter)
    for wrong, right in pairs:
        counts[wrong][merges.get(right, right)] += 1

    canon = {merges.get(r, r) for _, r in pairs} | set(merges.values())
    resolved = {}
    for wrong in sorted(counts):
        c = counts[wrong]
        if wrong in merges:                      # variant spelling of a word
            resolved[wrong] = merges[wrong]
            continue
        if wrong in canon:                       # valid word -> itself
            resolved[wrong] = wrong
            extra = {t: n for t, n in c.items() if t != wrong}
            if extra:
                report.append(f"valid word '{wrong}' also mapped to {extra} -> dropped")
            continue
        target, n = c.most_common(1)[0]
        if n / sum(c.values()) >= majority:
            resolved[wrong] = target
            if len(c) > 1:
                report.append(f"'{wrong}' kept -> {target} (votes {dict(c)})")
        else:
            report.append(f"'{wrong}' AMBIGUOUS {dict(c)} -> dropped")
    return resolved, canon, report


def edits(word):
    """All single realistic romanization / typing edits of a word."""
    out = set()
    n = len(word)
    swaps = [("aa", "a"), ("a", "aa"), ("ee", "e"), ("ee", "i"), ("e", "ee"),
             ("ii", "i"), ("i", "ii"), ("oo", "u"), ("u", "uu"), ("u", "o"),
             ("o", "u"), ("dh", "d"), ("d", "dh"), ("th", "t"), ("t", "th"),
             ("ch", "chh"), ("v", "w")]
    for old, new in swaps:
        start = 0
        while True:
            i = word.find(old, start)
            if i < 0:
                break
            out.add(word[:i] + new + word[i + len(old):])
            start = i + 1
    for i in range(1, n - 1):                    # single <-> double consonant
        ch = word[i]
        if ch not in VOWELS and word[i - 1] in VOWELS and word[i + 1] in VOWELS:
            out.add(word[:i] + ch + word[i:])
        if i + 1 < n and word[i] == word[i + 1] and ch not in VOWELS:
            out.add(word[:i] + word[i + 1:])
    for i in range(n - 1):                       # typing slips
        out.add(word[:i] + word[i + 1] + word[i] + word[i + 2:])
    for i in range(n):
        out.add(word[:i] + word[i + 1:])
        out.add(word[:i] + word[i] + word[i:])
    out.discard(word)
    return out


def make_variant(word, rng):
    first = sorted(edits(word))
    if not first:
        return None
    v = rng.choice(first)
    if rng.random() < 0.5:
        second = sorted(edits(v))
        if second:
            v = rng.choice(second)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=".")
    ap.add_argument("--out", default="clean_data")
    ap.add_argument("--files", nargs="*", default=DEFAULT_FILES)
    ap.add_argument("--merges", default="merges.txt")
    ap.add_argument("--test-frac", type=float, default=0.15)
    ap.add_argument("--dev-frac", type=float, default=0.10)
    ap.add_argument("--keep-train", nargs="*", default=["bagunnanu", "namaste", "hello"],
                    help="words that must stay in the training set")
    ap.add_argument("--min-test-typos", type=int, default=5,
                    help="a word needs this many real typos to be held out for testing")
    ap.add_argument("--variants", type=int, default=12, help="synthetic typos per word")
    ap.add_argument("--min-aug-len", type=int, default=4)
    ap.add_argument("--majority", type=float, default=0.8)
    ap.add_argument("--seed", type=int, default=13)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)

    pairs = load_pairs(a.data, a.files)
    merges = load_merges(a.merges)
    resolved, canon, report = resolve(pairs, merges, a.majority)
    print(f"raw lines {len(pairs)} | unique inputs after resolving {len(resolved)} "
          f"| canonical words {len(canon)}")

    for w in canon:                              # every word maps to itself
        resolved[w] = w

    by_word = collections.defaultdict(list)
    for wrong, right in resolved.items():
        by_word[right].append(wrong)

    words = sorted(canon)
    keep = set(a.keep_train)
    # Only words with enough real typos make a meaningful test set.
    eligible = [w for w in words
                if len(w) >= 5 and w not in keep
                and sum(1 for x in by_word[w] if x != w) >= a.min_test_typos]
    rng.shuffle(eligible)
    n_test = min(len(eligible), max(1, math.ceil(a.test_frac * len(words))))
    test_words = set(eligible[:n_test])
    train_words = [w for w in words if w not in test_words]

    train, dev, test = [], [], []
    for w in sorted(test_words):
        test += [(x, w) for x in sorted(by_word[w])]
    for w in sorted(train_words):
        typos = sorted(x for x in by_word[w] if x != w)
        rng.shuffle(typos)
        n_dev = int(round(a.dev_frac * len(typos)))
        dev += [(x, w) for x in typos[:n_dev]]
        train += [(x, w) for x in typos[n_dev:]] + [(w, w)]

    taken = set(resolved)                        # every real input, all splits
    synthetic = 0
    for w in sorted(train_words):
        if len(w) < a.min_aug_len:
            continue
        made = 0
        for _ in range(400):
            if made >= a.variants:
                break
            v = make_variant(w, rng)
            if v and len(v) >= 2 and v not in taken and v not in canon:
                taken.add(v)
                train.append((v, w))
                made += 1
                synthetic += 1

    # sanity checks: a valid word never maps elsewhere, inputs are unique
    seen = {}
    for x, y in train + dev + test:
        assert seen.setdefault(x, y) == y, f"conflict for {x}"
        if x in canon:
            assert x == y, f"valid word {x} maps to {y}"
    train_inputs = {x for x, _ in train}
    assert not any(x in train_inputs for x, _ in dev + test), "leak into dev/test"

    rng.shuffle(train)
    for name, rows in (("train.txt", train), ("dev.txt", dev), ("test.txt", test)):
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.writelines(f"{x} {y}\n" for x, y in rows)
    with open(os.path.join(a.out, "words_by_split.txt"), "w", encoding="utf-8") as f:
        for w in sorted(train_words):
            f.write(f"train {w}\n")
        for w in sorted(test_words):
            f.write(f"test {w}\n")
    with open(os.path.join(a.out, "cleaning_report.txt"), "w", encoding="utf-8") as f:
        f.write("Merges applied:\n")
        f.writelines(f"  {k} -> {v}\n" for k, v in sorted(merges.items()))
        f.write("\nConflict handling:\n")
        f.writelines(f"  {line}\n" for line in report)

    print(f"train {len(train)} ({synthetic} synthetic) | dev {len(dev)} | test {len(test)}")
    print(f"train words {len(train_words)} | held-out test words {len(test_words)}: "
          f"{sorted(test_words)}")
    print(f"wrote {a.out}/ (train.txt, dev.txt, test.txt, words_by_split.txt, cleaning_report.txt)")


if __name__ == "__main__":
    main()