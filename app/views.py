from .models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import requests
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
import requests
import nltk
import tweepy
import folium
import geocoder
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# Create your views here.


ckey="7h38tcEM8IO8id2htVXO9NDoW"
csecret="A9zfCDyM8mx7P2LBaC9rkCIgoOV3P71ZCajKbn2l0tt4EnkObk"
atoken="2611228746-JSr7EbtntCKlcAjZl5PkvVFxq8sYyzhamjvYYXg"
asecret="45c3EKZBxdI86ssyoR3gypx0ffIZGFyjlgcsznft2SToD"

def calculate_quora_score():
    answers_assam = get_data('assamciti')
    scores_assam = getscore(answers_assam)
    event_assam = Quora(event="Citizenship Bill",score=str(scores_assam))
    event_assam.save()
    answers_rafale = get_data('rafale_quora')
    scores_rafale = getscore(answers_rafale)
    event_rafale = Quora(event='Rafale Deal',score=str(scores_rafale))
    event_rafale.save()
    answers_ram = get_data('ram_mandir')
    scores_ram = getscore(answers_ram)
    event_ram = Quora(event='Ram Mandir',score=str(scores_ram))
    event_ram.save()

def getscore(sentences):
    c = neg = neu = pos = 0
    l = len(sentences)
    for sentence in sentences:
       ss = sid.polarity_scores(sentence)
       c += ss['compound']
       neg += ss['neg']
       neu += ss['neu']
       pos += ss['pos']
    return c/l, neg/l, neu/l, pos/l

def get_data(x):
    with open('app/data/' + x + '.json', encoding='utf8') as f:
       data = json.load(f)

    print(data)
    #answers = []
    # for k,v in data.items():
    #     answers.append(data[k]["Answers"])
    # print(answers)
    return data["1"]["Answers"]

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

def get_quora_data(request):
    calculate_quora_score()
    query_set = Quora.objects.all()
    return render(request,'app/quorascore.html',{'events':query_set})


#consumer key, consumer secret, access token, access secret.


def bot(request):
    print("Hi")
    if request.method == 'POST':
            global sign
            reply = request.POST.get('reply', '')
            print(reply)
            pos_neg = reply.split('-')
            reply = pos_neg[0]
            try:
                sign = pos_neg[1]
            except Exception as e:
                sign = ""
            print(sign)
            global list_of_tweets
            global i
            flag = True
            twitterStream = Stream(auth, listener())
            twitterStream.filter(track=[reply])
            print(list_of_tweets)
            block = []
            for j in range(len(list_of_tweets)):
                url = "https://api.twitter.com/1.1/statuses/oembed.json"
                params = dict(
                id = list_of_tweets[j]
                )
                resp = requests.get(url=url, params=params)
                data = resp.json()
                try:
                    aayu = data["html"].replace("<script async src=\"https://platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>","")
                    block.append(aayu)
                except Exception as e:
                    pass
            list_of_tweets = []
            i = 0
            sign = ""
            return render(request, 'app/bot.html', {'reply':reply, 'flag':flag,'block':block})
    else:
            flag = False
            return render(request, 'app/bot.html', {'flag':flag})
            print(request.method)


i = 0
list_of_tweets = []
sign = ""

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

class listener(StreamListener):
    def on_data(self, data):
        global i
        global list_of_tweets
        global sign
        data = json.loads(data)
        try:
            if data["id"] != ' ':
                print(data["text"])
                ss = sid.polarity_scores(data["text"])
                if sign == "p" and ss['compound']>=0:
                    list_of_tweets.append(data["id"])
                    print("positiveeeeeeee")
                    i = i + 1
                elif sign == "n" and ss['compound']<=0:
                    list_of_tweets.append(data["id"])
                    print("negativeeeeeee")
                    i = i + 1
                elif sign == "":
                    list_of_tweets.append(data["id"])
                    print("signlessssssss")
                    i = i + 1
        except Exception as e:
            pass
        if i<10:
            return True
        else:
            return False

    def on_error(self, status_code):
        if status_code == 420:
            return False

def gettwitterscore(term, count = 400):
   data = gettwitterresults(term, items=count)
   l = len(data)
   print(l)
   posloc = []
   negloc = []
   sentences = []
   c = neg = neu = pos = 0
   for tweet in data:
       json = tweet._json
       text = tweet.full_text
       sentences.append(text)
       ss = sid.polarity_scores(text)
       fc = json['favorite_count']
       rt = json['retweet_count']

       event = term
       location = json['user']['location']
       score_pos = ss['pos']
       score_neg = ss['neg']
       tweet_id = json['id']
       tweet = Twitter(tweet_id=tweet_id,event=event,location=location,score_pos=score_pos,score_neg=score_neg)
       print(tweet)
       tweet.save()

       sums = int((fc + rt)/500)
       l += sums
       if ss['compound'] >= 0:
           posloc.append(json['user']['location'])
       else:
           negloc.append(json['user']['location'])
       c += ss['compound'] * sums
       neg += ss['neg'] * sums
       neu += ss['neu'] * sums
       pos += ss['pos'] * sums

   print(l)
   event_name = term
   score = c/l
   pos_score = pos/l
   neg_score = neg/l
   neu_score = neu/l
   event = Event(event_name=event_name,score=score,pos_score=pos_score,neg_score=neg_score,neu_score=neu_score)
   event.save()
   #return c/l, neg/l, neu/l, pos/l, sentences, posloc, negloc



def gettwitterresults(term, items=400):

   auth = tweepy.OAuthHandler("7h38tcEM8IO8id2htVXO9NDoW", "A9zfCDyM8mx7P2LBaC9rkCIgoOV3P71ZCajKbn2l0tt4EnkObk")
   auth.set_access_token("2611228746-JSr7EbtntCKlcAjZl5PkvVFxq8sYyzhamjvYYXg", "45c3EKZBxdI86ssyoR3gypx0ffIZGFyjlgcsznft2SToD")

   api = tweepy.API(auth)
#     query = term + " -@ -filter:retweets -filter:media -filter:links -filter:replies"
   query = term
   searched_tweets = [status for status in tweepy.Cursor(api.search, q=query , lang='en', show_users = False,
                                                         tweet_mode='extended').items(items)]

   return searched_tweets

#     for tweet in searched_tweets:
#         pprint(tweet._json)
#         print(tweet.full_text)
#         print("-"*100)


def tweet_view(request):
    gettwitterscore('Narendra Modi')

    tweets = Twitter.objects.all()
    return render(request,'app/quorascore.html',{'tweets':tweets})

def events(request, id):
    event = Event.objects.get(id=id)
    event_name = event.event_name
    tweets = Twitter.objects.filter(event=event_name)
    quora = Quora.objects.get(event=event_name)
    quora_score = eval(quora.score)[0]
    event_score = event.score
    quo_eve = [quora_score, event_score]
    print(quo_eve)
    tweet_pos = event.pos_score
    tweet_neg = event.neg_score
    tweet_neu = event.neu_score
    score_list = [tweet_pos, tweet_neg, tweet_neu]
    posloc = []
    negloc = []
    score = []
    for tweet in tweets:
        sc = {'x': tweet.score_pos, 'y': tweet.score_neg}
        score.append(sc)
        if sc['x'] > sc['y']:
            posloc.append(tweet.location)
        else:
            negloc.append(tweet.location)
    context = {
        'event_name': event_name,
        'event_score': event_score,
        'posloc': posloc,
        'negloc': negloc,
        'score': score,
        'score_list':score_list,
        'quo_eve':quo_eve
    }
    if event_name == "Rafale Deal":
        txt = 'app/maprafale.html'
    elif event_name == "Ram Mandir":
        txt = 'app/mapram.html'
    else:
        txt = 'app/mapciti.html'
    return render(request, txt ,context)

def map(request):
    # m = folium.Map(location=[21.146633,  79.088860], zoom_start=5)
    # queryset = Twitter.objects.all().filter(event = 'Rahul Gandhi')
    # locs = []
    # for query in queryset:
    #     locs.append(query.location)
    # print(len(locs))
    # for index, loc in enumerate(locs):
    #     if index>200:
    #         break
    #     try:
    #         print(loc)
    #         g = geocoder.location(loc)
    #         folium.Marker(
    #             location=[g.lat, g.lng],
    #             popup='INC',
    #             icon=folium.Icon(color='green', icon='monero')
    #         ).add_to(m)
    #     except Exception as e:
    #         print(e)
    # queryset2 = Twitter.objects.all().filter(event = 'Narendra Modi')
    # locs2 = []
    # for query in queryset2:
    #     locs2.append(query.location)
    # print(len(locs2))
    # for index, loc in enumerate(locs2):
    #     if index>200:
    #         break
    #     try:
    #         print(loc)
    #         g = geocoder.location(loc)
    #         folium.Marker(
    #             location=[g.lat, g.lng],
    #             popup='BJP',
    #             icon=folium.Icon(color='orange', icon='monero')
    #         ).add_to(m)
    #     except Exception as e:
    #         print(e)

    # m.save('app/templates/app/mapteset2.html')
    # fil= open('app/templates/app/mapteset2.html',"r")
    # contents = fil.read()
    # fil.close()
    # f = open('app/templates/app/mapteset.html',"w+")
    # f.write('{% extends "app/map.html" %}')
    # f.write('{% block mapteset %}')
    # f.write(contents)
    # f.write("{% endblock %}")
    # f.close()
    return render(request, 'app/mapteset.html', {})
