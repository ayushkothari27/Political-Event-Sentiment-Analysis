from django.contrib import admin
from .models import Quora,Twitter,Event
# Register your models here.
admin.site.register(Quora)
admin.site.register(Twitter)
admin.site.register(Event)
