import requests

def get_news(api_key):
    try:
        response = requests.get(f"https://newsapi.org/v2/everything?q=AI+art&apiKey={api_key}")
        return response.json()["articles"][:3]
    except:
        return []
