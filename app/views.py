from .models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
import requests
import nltk
import tweepy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

ckey="7h38tcEM8IO8id2htVXO9NDoW"
csecret="A9zfCDyM8mx7P2LBaC9rkCIgoOV3P71ZCajKbn2l0tt4EnkObk"
atoken="2611228746-JSr7EbtntCKlcAjZl5PkvVFxq8sYyzhamjvYYXg"
asecret="45c3EKZBxdI86ssyoR3gypx0ffIZGFyjlgcsznft2SToD"

def calculate_quora_score():
    answers_assam = get_data('assamciti')
    scores_assam = getscore(answers_assam)
    event_assam = Quora(event="Citizenship Bill And Assam",score=str(scores_assam))
    event_assam.save()
    answers_rafale = get_data('rafale_quora')
    scores_rafale = getscore(answers_rafale)
    event_rafale = Quora(event='Rafale Deal',score=str(scores_rafale))
    event_rafale.save()
    answers_ram = get_data('ram_mandir')
    scores_ram = getscore(answers_ram)
    event_ram = Quora(event='Ram Mandir Controversy',score=str(scores_ram))
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


def get_quora_data(request):
    #calculate_quora_score()
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
    gettwitterscore('Rahul Gandhi')

    tweets = Twitter.objects.all()
    return render(request,'app/quorascore.html',{'tweets':tweets})
