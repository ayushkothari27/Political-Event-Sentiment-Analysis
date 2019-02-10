from django.shortcuts import render, redirect
import requests

def dashboard(request):
    return render(request, 'app/dashboard.html', {})

def news(request):
    times_of_india_news = requests.get("https://newsapi.org/v2/everything?q=politics&apiKey=22318c0edb3f412fb605062a091e4239")
    times_of_india_data =  dict(times_of_india_news.json())
    toi_articles = times_of_india_data['articles']

    google_news = requests.get("https://newsapi.org/v2/top-headlines?sources=google-news-in&apiKey=22318c0edb3f412fb605062a091e4239")
    google_data = dict(google_news.json())
    google_articles = google_data['articles']

    articles_json = []
    articles_json = toi_articles + google_articles

    articles = []
    for article in articles_json:
        articles.append(Article(title = article['title'], description = article['description'],url = article['url'],image_url=article['urlToImage']))
        print(article)
    context = {'articles':articles}
    print("-"*100)

    return render(request, 'app/news.html', context)

class Article():
    def __init__(self,title,description,url,image_url):
        self.title = title
        self.description = description
        self.url = url
        self.image_url = image_url

    def __str__(self):
        return self.url
