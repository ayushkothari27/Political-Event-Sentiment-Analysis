from django.shortcuts import render
import nltk
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .models import Quora,Twitter
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

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
