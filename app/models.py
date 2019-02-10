from django.db import models

# Create your models here.

class Twitter(models.Model):
    event = models.CharField(max_length=200, blank=True, null=True)
    tweet_id = models.CharField(max_length=200, blank=True, null=True)
    score_pos = models.CharField(max_length=200, blank=True, null=True)
    score_neg = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.event

class Quora(models.Model):
    event = models.CharField(max_length=200, blank=True, null=True)
    score = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
       return self.event


class Event(models.Model):
    event_name = models.CharField(max_length=200, blank=True, null=True)
    score = models.CharField(max_length=200, blank=True, null=True)
    pos_score = models.CharField(max_length=200, blank=True, null=True)
    neu_score = models.CharField(max_length=200, blank=True, null=True)
    neg_score = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
       return self.event_name
