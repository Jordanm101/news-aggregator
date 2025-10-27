from fastapi import FastAPI
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv() #loading environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


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

def summarize_article(content: str) -> str:
    if not content:
        return "No content to summarize."
    
    #what prompt to send to the model
    prompt = f"Summarize this news article in 2-3 concise sentences:\n\n{content}"
    
    #calling the OpenAI API to summarize the article
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return "Summary unavailable."
    
@app.get("/news/summary")
def summarize_news(query: str = "technology"):
    # Fetch top articles by topic
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Failed to fetch news", "status": response.status_code}

    data = response.json()
    articles = data.get("articles", [])[:3]  # limit to top 3 articles

    results = []
    for a in articles:
        title = a.get("title")
        description = a.get("description") or ""
        content = a.get("content") or description  # fallback if content empty
        url = a.get("url")

        # Combine and summarize
        article_text = f"Title: {title}\n{content}"
        summary = summarize_article(article_text)

        results.append({
            "title": title,
            "summary": summary,
            "url": url
        })

    return {"topic": query, "summaries": results}


