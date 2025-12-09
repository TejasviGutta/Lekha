from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import main

app = FastAPI(title= "Lekh.AI Backend")

class CorrectRequest(BaseModel):
    word:str

class CorrectResponse(BaseModel):
    original: str
    corrected: str

@app.post("/correct", response_model=CorrectResponse)

def correctWord(req: CorrectRequest):
    word = req.word.strip()
    if not word:
        raise HTTPException(status_code = 400, detail="word cannot be empty")
    
    corrected = main.correctWord(word)

    if word not in main.userDict:
        main.userDict[word] = corrected
        with open(main.UserDataFile, "a", encoding="utf-8") as f:
            f.write(f"{word} {corrected}\n")
        if len(main.userDict) % 50 == 0:
            main.fine_tune_on_user_data()
    return CorrectResponse(original=word, corrected=corrected)
@app.get("/")
def root():
    return{"message": "Lekh.AI backend run"}
