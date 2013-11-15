from django.contrib import admin
from apps.main.models import TwitterScheduled, TwitterAuth, TwitterSearch, Settings, TwitterCompetitor, TwitterInfo, OldTweet


admin.site.register(TwitterScheduled)
admin.site.register(TwitterAuth)
admin.site.register(TwitterSearch)
admin.site.register(Settings)
admin.site.register(TwitterInfo)
admin.site.register(TwitterCompetitor)
admin.site.register(OldTweet)
