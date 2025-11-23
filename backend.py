from fastapi import FastAPI
from pydantic import BaseModel
import torch

from main import correctWord, model
app = FastAPI()

UserFolder = "userdata"
os.makdirs(UserFolder, exist_ok= True)

from main import sequenceToSequence, correctWord, charToIndex, indexToChar, wordToSequenceInput, wordToSequenceOutput, maxLenInput, maxLenOutput

model = sequenceToSequence((len(charToIndex), 128, 256))
model.load_state_dict(torch.load("telugu_autocorrect8.pth", map_location= "cpu"))
model.eval()


## need to do request of body ###
##PHONE COMES FROM REQUEST OF BODY!!!

def loadUserDict(phone):
    path = f"{UserFolder}/{phone}.json"

    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
        return {}
    with open(path, "r") as f:
        return json.load(f)
    
def saveUserDict(phone, data):
    path = f"{UserFolder}/{phone}.json"
    with open(path, "w") as f: 
        json.dump(data, f, indent=4)

def predWord(req: PredictionRequest):
    
    