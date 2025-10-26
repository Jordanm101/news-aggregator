from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv

load_dotenv() #loading environment variables from .env file

app = FastAPI() #iinitialize FastAPI app

NEWS_API_KEY = os.getenv("NEWS_API_KEY") #getting api key from .env

@app.get("/") #health check endpoint
def read_root():
    return {"status": "ok", "message": "Hello from News Aggregator!"}

#main endpoint to fetch news articles
@app.get("/news")
def get_news(country: str = "us"):
    #fetching news from specified country
    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    
    #handling failed requests
    if response.status_code != 200:
        return {"error": "Failed to fetch news", "status": response.status_code}
    
    data = response.json()
    
    # clean and formating the articles 
    articles = [
        {
            "title": a.get("title"), 
            "source": a.get("source", {}).get("name"), 
            "url": a.get("url"),
        }
        for a in data.get("articles", [])
        if a.get("title") and a.get("url") #this only keeps valid articles
    ]
    
    #logging the number of articles fetched
    print(f"Fetched {len(articles)} articles for country: {country}")
    
    return {"total": len(articles), "articles": articles}

@app.get("/news/topic")
def get_news_by_topic(query: str = "technology"):
    #fetching news based on topic 
    
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWS_API_KEY}"
    
    #making the request to news api
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Failed to fetch topic news", "status": response.status_code}

    data = response.json()

    articles = [
        {
            "title": a.get("title"),
            "source": a.get("source", {}).get("name"),
            "url": a.get("url"),
        }
        for a in data.get("articles", [])
        if a.get("title") and a.get("url")
    ]
    #logging the number of articles fetched
    print(f"Fetched {len(articles)} articles for topic: {query}")
    #returning the articles
    return {"topic": query, "total": len(articles), "articles": articles}

