from django.conf.urls import url
from . import views

app_name = 'app'

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
]
