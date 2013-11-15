# Create your views here.
from django.shortcuts import render, get_object_or_404
from apps.main.models import TwitterAuth, TwitterSearch, TwitterScheduled, TwitterCompetitor, TwitterInfo, OldTweet
from apps.main.models import TwitterAuthForm, TwitterSearchForm, TwitterScheduledForm, TwitterCompetitorForm
import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import tweepy
import urllib
import stripe
 
######  HELPERS  #####

def twitterapi(consumer_key, consumer_secret, access_token_key, access_token_secret):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token_key,access_token_secret)
	api = tweepy.API(auth)
	return api


######  VIEWS  #####

def index(request):
	return render(request, 'main/index.html',)

def payment(request):

	if request.method == 'POST':
		stripe.api_key = "sk_test_ChZBYMHbZLagr8DQdsqxcq9y"

		# Get the credit card details submitted by the form
		token = request.POST['stripeToken']

		# Create the charge on Stripe's servers - this will charge the user's card
		try:
		  charge = stripe.Charge.create(
		      amount=1000, # amount in cents, again
		      currency="usd",
		      card=token,
		      description="payinguser@example.com"
		  )
		except stripe.CardError, e:
		  # The card has been declined
		  pass


	return render(request, 'main/payment.html',)

@login_required() 
def home(request):
	return render(request, 'main/index.html',)

@login_required() 
def settings(request):
	if request.method=='POST':
		if 'addtwitter' in request.POST:
			form = TwitterAuthForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.user = request.user
				instance.save()
				return HttpResponseRedirect(reverse('apps.main.views.settings', args=()))

	else: form = TwitterAuthForm()

	context = {'form':form}
	return render(request, 'main/settings.html', context)

@login_required() 
def mytwitter(request):
	account = TwitterAuth.objects.get(user=request.user, twittername = 'MotivationDayQ')

	try: data = TwitterInfo.objects.get(twittername = account)
	except TwitterInfo.DoesNotExist: data = []

	tweets = OldTweet.objects.filter(twittername = account)


	if request.method=='GET' and 'pulltwitter' in request.GET:
		api = twitterapi(account.consumer_key, account.consumer_secret, account.access_token_key, account.access_token_secret)
		tweets = api.user_timeline()
		mentions = api.mentions_timeline()
		data = api.me()

		# try:
		# 	t = TwitterInfo.objects.get(twittername = account)
		# 	t.name = data.name 
		# 	t.followers_count = data.followers_count
		# 	t.favourites_count = data.favourites_count
		# 	t.friends_count = data.friends_count
		# 	t.id_str = data.id_str
		# 	t.location = data.location
		# 	t.profile_image_url = data.profile_image_url
		# 	t.statuses_count = data.statuses_count
		# 	t.screen_name= data.screen_name
		# 	t.save()

		# except TwitterInfo.DoesNotExist:
		# 	TwitterInfo.objects.create( twittername = account, name = data.name, followers_count = data.followers_count, avourites_count = data.favourites_count, riends_count = data.friends_count , 
		# 								id_str = data.id_str,location = data.location,profile_image_url = data.profile_image_url,statuses_count = data.statuses_count,screen_name= data.screen_name)


		TwitterInfo.objects.filter(twittername = account).delete()
		TwitterInfo.objects.create( twittername = account, name = data.name, followers_count = data.followers_count, favourites_count = data.favourites_count, friends_count = data.friends_count , 
										id_str = data.id_str,location = data.location,profile_image_url = data.profile_image_url,statuses_count = data.statuses_count,screen_name= data.screen_name)


		OldTweet.objects.filter(twittername=account).delete()
		OldTweet.objects.bulk_create([OldTweet(twittername=account,text=t.text, created_at=t.created_at, favorite_count = t.favorite_count, retweet_count=t.retweet_count, id_str=t.id_str) for t in tweets])


		context = {'tweets' : tweets, 'summarydata':data }
		return render(request, 'main/mytwitter.html', context)

	context = {'summarydata':data, 'tweets':tweets }
	return render(request, 'main/mytwitter.html', context)

@login_required() 
def twitterengage(request):
	account = TwitterAuth.objects.get(user=request.user, twittername = 'MotivationDayQ')

	if request.method=='GET' and 'searchtwitter' in request.GET:
		form = TwitterSearchForm(request.GET)
		if form.is_valid():
			api = twitterapi(account.consumer_key, account.consumer_secret, account.access_token_key, account.access_token_secret)
			encodedsearch = urllib.quote(form.cleaned_data['search'])
			searchresults = api.search(q=encodedsearch, count=50)
			context = {'searchresults' : searchresults, 'form':form}
			return render(request, 'main/twitterengage.html', context)

	# if request.method=='GET' and 'savesearch' in request.GET:
	# 	form = TwitterSearchForm(request.POST)
	# 	if form.is_valid():
	# 		searchresults = api.search(q=encodedsearch, count=50)
	# 		context = {'searchresults' : searchresults, 'form':form}
	# 		return render(request, 'main/twitterengage.html', context)

	if request.method=='POST':
		form = TwitterSearchForm()

		if 'tweet' in request.POST:
			api = twitterapi(account.consumer_key, account.consumer_secret, account.access_token_key, account.access_token_secret)
			tweetatid = request.POST['tweetatid']
			tweettext = request.POST['tweettext']
			api.update_status(status=tweettext, in_reply_to_status_id= tweetatid)
			context = {'form':form}
			return render(request, 'main/twitterengage.html', context)


	else: form = TwitterSearchForm()
	context = {'form':form}
	return render(request, 'main/twitterengage.html',context)

@login_required() 
def twitterschedule(request):
	account = TwitterAuth.objects.get(user=request.user, twittername = 'MotivationDayQ')

	if request.method=='POST':
		if 'scheduletweet' in request.POST:
			form = TwitterScheduledForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.twittername = account
				instance.save()
				return HttpResponseRedirect(reverse('apps.main.views.twitterschedule', args=()))

	else: form = TwitterScheduledForm()

	context = {'form':form}	
	return render(request, 'main/twitterschedule.html',context)

@login_required() 
def twittercompetition(request):
	account = TwitterAuth.objects.get(user=request.user, twittername = 'MotivationDayQ')
	competitors = TwitterCompetitor.objects.filter(twittername = account)

	if request.method=='POST':
		if 'addcompetitor' in request.POST:
			form = TwitterCompetitorForm(account, request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.twittername = account
				instance.save()
				return HttpResponseRedirect(reverse('apps.main.views.twittercompetition', args=()))

	else: form = TwitterCompetitorForm(account)

	context = {'form':form, 'competitors':competitors}
	return render(request, 'main/twittercompetition.html', context)

@login_required() 
def twitteranalysis(request):
	account = TwitterAuth.objects.get(user=request.user, twittername = 'MotivationDayQ')

	if request.method=='GET' and 'timeanalysis' in request.GET:
		api = twitterapi(account.consumer_key, account.consumer_secret, account.access_token_key, account.access_token_secret)
		followers = api.me.followers
		context = {'followers' : followers }
		return render(request, 'main/twitterengage.html', context)

	return render(request, 'main/twitteranalysis.html',)
