from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import main
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title= "LekhAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

class CorrectRequest(BaseModel):
    word:str

class CorrectResponse(BaseModel):
    original: str
    corrected: str

class ConfirmRequest(BaseModel):
    original: str
    corrected: str

@app.post("/correct", response_model=CorrectResponse)

def correctWord(req: CorrectRequest):
    word = req.word.strip().lower()
    if not word:
        raise HTTPException(status_code = 400, detail="word cannot be empty")
    
    corrected = main.correctWord(word)
    return CorrectResponse(original=word, corrected=corrected)
@app.post("/confirm")

def confirmCorrection(req: ConfirmRequest, backgroundTasks: BackgroundTasks):
    original = req.original.strip().lower()
    corrected = req.corrected.strip().lower()

    if original in main.userDict:
        return{"status": "already saved"}
    
    main.userDict[original] = corrected
    with open(main.UserDataFile, "a", encoding = "utf-8") as f:
        f.write(f"{original} {corrected}\n")
    if len(main.userDict) % 25 == 0:
        backgroundTasks.add_task(main.fine_tune_on_user_data)

        return{"status": "saved"}
    
@app.get("/")
def root():
    return{"message": "LekhAI backend run"}