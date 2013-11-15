from django.conf.urls import patterns, url
from apps.main import views

 

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.home, name='home'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^payment/$', views.payment, name='payment'),
    url(r'^twitter/mytwitter/$', views.mytwitter, name='mytwitter'),
    url(r'^twitter/engage/$', views.twitterengage, name='twitterengage'),
    url(r'^twitter/schedule/$', views.twitterschedule, name='twitterschedule'),
    url(r'^twitter/competition/$', views.twittercompetition, name='twittercompetition'),
    url(r'^twitter/analysis/$', views.twitteranalysis, name='twitteranalysis'),
)



# saved searches
# save scheduled tweets --seperate date and time dropdowns
# get info on competitors
# get mentions
# add stripe, braintree
# learn about django celery for scheduling tweets
# make reply form
# sidebar to switch accounts


