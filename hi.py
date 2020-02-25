import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "A5pnZFkmPpneENHW8z3Wg", "isbns": "9781632168146"})
print(res.json())
