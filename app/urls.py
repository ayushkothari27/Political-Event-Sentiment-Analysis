from django.conf.urls import url
from . import views

app_name = 'app'

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^bot/$', views.bot, name='bot'),
    url(r'^events/(\d+)$', views.events, name='events'),
]
