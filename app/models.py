from django.db import models

# Create your models here.

class Twitter(models.Model):
    event = models.CharField(max_length=200, blank=True, null=True)
    tweet_id = models.CharField(max_length=200, blank=True, null=True)
    score = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

class Quora(models.Model):
    event = models.CharField(max_length=200, blank=True, null=True)
    score = models.CharField(max_length=200, blank=True, null=True)

class Event(models.Model):
    event_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.event_name
