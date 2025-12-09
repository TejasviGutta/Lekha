import torch
import torch.nn as nn
import torch.optim as optim
import random
import os

#reading text file
words = []
word_dict ={}
with open("training_balanced.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            wrong, right = line.split()
            words.append((wrong, right))
            word_dict[wrong] = right

##### YOU NEED TO COMPLETE THIS!!!!!!
UserDataFile = "userData.txt"
userDict = {}
if not os.path.exists(UserDataFile):
    open(UserDataFile, "w", encoding = "utf-8").close()

with open(UserDataFile, "r", encoding = "utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            wrong, right = line.split()
            userDict[wrong]= right


# collecting unique characters
chars = set()
for wrong, correct in words:
    chars.update(list(wrong))
    chars.update(list(correct))

# mappings
charToIndex = {c: i+1 for i, c in enumerate(sorted(chars))}
#padding token
charToIndex["<PAD>"] = 0
charToIndex["<SOS>"] = 1
charToIndex["<EOS>"] = 2

idx = 3
for c in sorted(chars):
    charToIndex[c] = idx
    idx+=1

indexToChar = {i:c for c, i in charToIndex.items()}
vocabSize = len(charToIndex) + 1

#set vocab size:
vocabSize = len(charToIndex); 

# converting words to sequences
def wordToSequenceInput(word, max_len):
    sequence = [charToIndex[c] for c in word]
    sequence += [charToIndex["<PAD>"]] * (max_len - len(sequence))
    return sequence

def wordToSequenceOutput(word, max_len):
    sequence = [charToIndex["<SOS>"]]
    sequence += [charToIndex[c] for c in word]
    sequence.append(charToIndex["<EOS>"])
    sequence += [0] * (max_len - len(sequence))
    return sequence


maxLenInput = max(len(wrong) for wrong,_ in words) 
maxLenOutput = max(len(correct) for _, correct in words) + 2

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

    def forward(self, source, target, teacher_forcing_ratio = 0.5):
        batchSize , seqlen = target.size()
        outputs = torch.zeros(batchSize, seqlen, vocabSize).to(source.device)

        embeddedSrc = self.embedding(source)
        _, (hidden, cell) = self.encoder((embeddedSrc))
        decoder_input = target[:, 0].unsqueeze(1)
        
        for t in range(1, seqlen):
            embedded = self.embedding(decoder_input)
            output, (hidden,cell) = self.decoder(embedded, (hidden, cell))
            prediction = self.fc(output)
            outputs[:, t, :] = prediction.squeeze(1)

            teacherForce = random.random() < teacher_forcing_ratio
            top1 = prediction.argmax(2)
            decoder_input = (target[:, t].unsqueeze(1) if teacherForce else top1)
        return outputs
        
    
embedding_dim = 128
hidden_dim = 256

model = sequenceToSequence(vocabSize, embedding_dim, hidden_dim)
criteria = nn.CrossEntropyLoss(ignore_index=charToIndex["<PAD>"])
optimize = torch.optim.Adam(model.parameters(), lr = 0.001)

def fine_tune_on_user_data():
    user_words = []
    with open(UserDataFile, "r", encoding = "utf-8") as f:
        for line in f:
            wrong, right = line.strip().split()
            user_words.append((wrong, right))

    if not user_words:
        return
    userInputs = torch.tensor([wordToSequenceInput(wrong, maxLenInput) for wrong, _ in user_words], dtype=torch.long)
    userTargets = torch.tensor([wordToSequenceOutput(correct, maxLenOutput) for _, correct in user_words], dtype=torch.long)
    optimize = torch.optim.Adam(model.parameters(), lr=0.0001)
    criteria = nn.CrossEntropyLoss(ignore_index=charToIndex["<PAD>"])
    for epoch in range(10):
        model.train()
        optimize.zero_grad()
        decoderInput = userTargets[:, :-1]
        decoderTarget = userTargets[:,1:]
        output = model(userInputs, decoderInput)
        loss = criteria(output.view(-1, vocabSize), decoderTarget.contiguous().view(-1))
        loss.backward()
        optimize.step()
    torch.save(model.state_dict(), "telugu_autocorrect_user.pth")

#training
num = 100
batch_size = 16
dataset_size = len(inputs)

for epoch in range(num):
    model.train()
    permutation = torch.randperm(dataset_size)

    for i in range (0, dataset_size, batch_size):
        optimize.zero_grad()
        indicies = permutation[i:i+batch_size]
        batchInputs = inputs[indicies]
        batchTargets = targets[indicies]

        output = model(batchInputs, batchTargets)
        output = output.view(-1, vocabSize)
        targetsF = batchTargets.contiguous().view(-1)

        loss = criteria(output, targetsF)
        loss.backward()
        optimize.step()

    if(epoch+1)%10 == 0:
        print(f"Epoch [{epoch + 1}/ {num}], Loss: {loss.item():.4f}")


def beamSearchDecode(model, seq, beamWidth = 3, maxLen = None):
    if maxLen is None:
        maxLen = maxLenOutput

    model.eval()
    seq_tensor = torch.tensor([seq], dtype = torch.long)
    with torch.no_grad():
        _, (hidden, cell) = model.encoder(model.embedding(seq_tensor))
        beams = [(0, [charToIndex["<SOS>"]], hidden, cell)]
        completed = []

        for _ in range(maxLen):
            new_beams = []
            for score, seqSoFar, h, c in beams:
                decoderInput = torch.tensor([[seqSoFar[-1]]], dtype=torch.long)
                emb = model.embedding(decoderInput)
                out, (hNew, cNew) = model.decoder(emb, (h,c))
                logits = model.fc(out[:, -1, :])
                probs = torch.log_softmax(logits, dim =-1).squeeze(0)
                topk = torch.topk(probs, beamWidth)
                for idx, logp in zip(topk.indices.tolist(), topk.values.tolist()):
                    newSeq = seqSoFar + [idx]
                    newScore = score + logp
                    if idx == charToIndex["<EOS>"]:
                        completed.append((newScore, newSeq))
                    else:
                        new_beams.append((newScore, newSeq, hNew, cNew))
            beams = sorted(new_beams, key = lambda x: x[0], reverse = True)[:beamWidth]
            if not beams:
                break
        completed = completed if completed else beams
        completed = sorted(completed, key = lambda x: x[0], reverse = True)
        bestSeq = completed[0][1]
        decoded = ""
        for idx in bestSeq:
            if idx not in [charToIndex["<SOS>"], charToIndex["<PAD>"], charToIndex["<EOS>"]]:
                decoded += indexToChar[idx]
                
        return decoded

# testing
def correctWord(word, maxDecodeLen=None):
    if word in userDict:
        return userDict[word]
    
    if word in word_dict:
        return word_dict[word]
    
    seq = wordToSequenceInput(word, maxLenInput)
    input_tensor = torch.tensor([seq], dtype=torch.long)

    if maxDecodeLen is None:
        maxDecodeLen = maxLenOutput
    
    predictedWord = "" 
    with torch.no_grad():
        _, (hidden, cell) = model.encoder(model.embedding(input_tensor))
        decoderInput = torch.tensor([[charToIndex["<SOS>"]]], dtype=torch.long)
        predictedWord=""

        for _ in range(maxDecodeLen):
            emb = model.embedding(decoderInput)
            output, (hidden, cell) = model.decoder(emb, (hidden, cell))
            logit = model.fc(output[:, -1, :])
            predIndex = int(torch.argmax(logit, dim=1).item())

            if predIndex == charToIndex["<EOS>"]:
                break
            if predIndex not in [charToIndex["<PAD>"], charToIndex["<SOS>"]]:
                predictedWord += indexToChar[predIndex]
            decoderInput = torch.tensor([[predIndex]], dtype=torch.long)
    return predictedWord

if __name__ == "__main__":
    print("Modle loaded. Used by backend.")
