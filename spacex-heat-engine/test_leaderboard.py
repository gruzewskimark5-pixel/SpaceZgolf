import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Fetching Leaderboard...")
res = requests.get(f"{BASE_URL}/leaderboard")
if res.status_code == 200:
    for row in res.json():
        print(f"{row['name']} ({row['role']}) - HI: {row['hi']}, CES: {row['ces']}")
else:
    print(f"Error {res.status_code}: {res.text}")
