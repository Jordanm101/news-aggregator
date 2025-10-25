from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Hello from News Aggregator!"}

@app.get("/news")
def get_news(country: str = "us"):
    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    articles = [
        {"title": a["title"], "source": a["source"]["name"], "url": a["url"]}
        for a in data.get("articles", [])
    ]
    return {"total": len(articles), "articles": articles}
