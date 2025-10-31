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
            words.append((wrong, right))


# collecting unique characters
chars = set()
for wrong, correct in words:
    chars.update(list(wrong))
    chars.update(list(correct))

# mappings
charToIndex = {c: i+1 for i, c in enumerate(sorted(chars))}
#padding token
charToIndex["<PAD>"] = 0
charToIndex["<EOS>"] = len(charToIndex)

indexToChar = {i:c for c, i in charToIndex.items()}

#set vocab size:
vocabSize = len(charToIndex); 

# converting words to sequences
def wordToSequenceInput(word, max_len):
    sequence = [charToIndex[c] for c in word]
    sequence += [0] * (max_len - len(sequence))
    return sequence

def wordToSequenceOutput(word, max_len):
    sequence = [charToIndex[c] for c in word]
    sequence.append(charToIndex["<EOS>"])
    sequence += [0] * (max_len - len(sequence))
    return sequence


maxLenInput = max(len(wrong) for wrong,_ in words) 
maxLenOutput = max(len(correct) for _, correct in words) + 1

input_sequences = [wordToSequenceInput(wrong, maxLenInput) for wrong , _ in words]
target_sequences = [wordToSequenceOutput(correct, maxLenOutput) for _, correct in words]

inputs = torch.tensor(input_sequences, dtype=torch.long)
targets = torch.tensor(target_sequences, dtype=torch.long)

#The actual model itself
class sequenceToSequence(nn.Module):
    def __init__(self, vocabSize, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocabSize, embed_dim)
        self.encoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocabSize)

    def forward(self, source, target):
        _, (hidden, cell) = self.encoder(self.embedding(source))
        outputs, _ = self.decoder(self.embedding(target), (hidden, cell))
        predictions = self.fc(outputs)
        return predictions
    
embedding_dim = 64
hidden_dim = 128

model = sequenceToSequence(vocabSize, embedding_dim, hidden_dim)
criteria = nn.CrossEntropyLoss(ignore_index=0)
optimize = torch.optim.Adam(model.parameters(), lr = 0.001)

#training
num = 100

for epoch in range(num):
    model.train()
    optimize.zero_grad()
    
    output = model(inputs, targets)
    output = output.view(-1, vocabSize)

    targetsF = targets.view(-1)

    loss = criteria(output, targetsF)
    loss.backward()

    optimize.step()

    if(epoch+1)%10 == 0:
        print(f"Epoch [{epoch + 1}/ {num}], Loss: {loss.item():.4f}")


# testing
model.eval()

def correctWord(word):
    seq = wordToSequenceInput(word, maxLenInput)
    input_tensor = torch.tensor([seq], dtype=torch.long)

    with torch.no_grad():
        output = model(input_tensor, input_tensor)

    predictionI = output.argmax(2).squeeze().tolist()

    predicted_word = ""
    for i in predictionI: 
        if i == charToIndex["<EOS>"]:
            break; 
        if i != 0:
            predicted_word += indexToChar[i]
    

    return predicted_word

testWord = ["bagnunnanu", "nee", "emthi"]
for w in testWord:
    print(w, "->", correctWord(w))


#save
torch.save(model.state_dict(), "telugu_autocorrect2.pth")
print("model saved as telugu_autocorrect2.pth")
