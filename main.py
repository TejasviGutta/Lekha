import torch
import torch.nn as nn
import torch.optim as optim

#reading text file
words = []
with open("training.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            wrong, right = line.split()
            words.append({wrong, right})


# collecting unique characters
chars = set()
for wrong, correct in words:
    chars.update(list(wrong))
    chars.update(list(correct))

# mappings
charToIndex = {c: i+1 for i, c in enumerate(sorted(chars))}
#padding token
charToIndex["<PAD>"] = 0

indexToChar = {i:c for c, i in charToIndex.items()}

#set vocab size:
vocabSize = len(charToIndex); 

# converting words to sequences
def wordToSequence(word, max_len):
    sequence = [charToIndex[c] for c in word]
    sequence += [0] * (max_len - len(sequence))

    return sequence

maxLenInput = max(len(pair[0]) for pair in words)
maxLenOutput = max(len(pair[1]) for pair in words)

input_sequences = [wordToSequence(pair[0], maxLenInput) for pair in words]
target_sequences = [wordToSequence(pair[1], maxLenOutput) for pair in words]

inputs = torch.tensor(input_sequences, dtype=torch.long)
targets = torch.tensor(target_sequences, dtype=torch.long)

#The actual model itself
class sequenceToSequence(nn.module):
    def initialize(self, vocabSize, embed_dim, hidden_dim):
        super().initialize()
    






# BELOW IS TESTING THE CONVERTING WORDS TO SEQUENCES
# test = ["bagnunnanu", "nee", "emthi"]
# for word in test:
#     seq = wordToSequence(word, maxLenInput)
#     print(f"Word:{word} -> Sequence: {seq}")

# testTensors = torch.tensor([wordToSequence(word, maxLenInput) for word in test], dtype = torch.long)
# print("Tensor Shape:", testTensors.shape)
# print(testTensors)

# for seq in testTensors:
#     wordFromSequence = "".join([indexToChar[i.item()] for i in seq if i.item() != 0])

#     print("Recovered word:", wordFromSequence)
