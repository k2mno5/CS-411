from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.display_random, name='random'),
]
