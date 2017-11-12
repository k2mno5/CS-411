from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/following/checkList$',views.getFollowingStatus),
    url(r'^post/vote/checkList$',views.getVoteStatus),
]
