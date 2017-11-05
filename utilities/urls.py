from django.conf.urls import url
from . import views

# remember to restart apache server to keep url up to date
urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^post/vote/(?P<postID>[0-9]+)/(?P<postType>[0-1]{1})/(?P<userID>[0-9]+)/(?P<voteStatus>[0-2]{1})/$',views.updateVoteStatus),
    url(r'^userUpdateRandom/$', views.getUserUpdate_random),
]