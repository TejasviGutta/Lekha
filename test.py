import requests

# URL of your running FastAPI backend
BASE_URL = "http://127.0.0.1:8000"

def test_correct_word(word):
    url = f"{BASE_URL}/correct"
    payload = {"word": word}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Original: {data['original']}, Corrected: {data['corrected']}")
    else:
        print(f"Error {response.status_code}: {response.json()}")

if __name__ == "__main__":
    test_words = ["ella", "unavu", "emthi", "perru", "baagunnanu"]
    for w in test_words:
        test_correct_word(w)
