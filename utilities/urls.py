from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/following/checkList$',views.getFollowingStatus),
    url(r'^post/vote/checkList$',views.getVoteStatus),
    url(r'^user/status/(?P<userID>[0-9]+)/(?P<showActivities>[01]{1})',views.getUserStatus),
    url(r'^user/following/(?P<userID>[0-9]+)/(?P<page>[0-9]+)', views.getFollowingActivities),
    url(r'^user/(?P<requestType>followings|followers)/(?P<userID>[0-9]+)/(?P<page>[0-9]+)/(?P<showDetail>[01]{1})', views.getFollows),
]
