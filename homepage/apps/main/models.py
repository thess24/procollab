from django.db import models
from django.forms import ModelForm, Textarea
from django import forms
from django.contrib.auth.models import User
import tweepy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import StrictButton, PrependedText



class Settings(models.Model):

	PAY_TIER_LIST = (
		('Free', 'Free'), 
		('Beginner', 'Beginner'),
		('Apprentice', 'Apprentice'),
		('Master', 'Master'),
		('Sensei', 'Sensei'),
		)

	user = models.OneToOneField(User)
	company = models.CharField(max_length=100)
	paytier = models.CharField(max_length=100, choices=PAY_TIER_LIST)
	twitteraccts = models.IntegerField()
	twittersavedsearch = models.IntegerField()
	twitterschedule = models.BooleanField()

	def __unicode__(self):
		return self.user

class TwitterAuth(models.Model):
	user = models.ForeignKey(User)
	twittername = models.CharField(max_length=140)
	consumer_key = models.CharField(max_length=200)
	consumer_secret = models.CharField(max_length=200)
	access_token_key = models.CharField(max_length=200)
	access_token_secret = models.CharField(max_length=200)

	def __unicode__(self):
		return self.twittername

class TwitterSearch(models.Model):
	twittername = models.ForeignKey(TwitterAuth)
	search = models.CharField(max_length=1000)

	def __unicode__(self):
		return self.twittername.twittername

class TwitterScheduled(models.Model):
	twittername = models.ForeignKey(TwitterAuth)
	tweet = models.CharField(max_length=200)
	time = models.DateTimeField()
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.twittername.twittername	

class TwitterCompetitor(models.Model):
	twittername = models.ForeignKey(TwitterAuth)
	competitorname = models.CharField(max_length=200)
	competitorhandle = models.CharField(max_length=100)

	def __unicode__(self):
		return self.twittername.twittername

class TwitterInfo(models.Model):
	twittername = models.ForeignKey(TwitterAuth)
	name = models.CharField(max_length=500)
	followers_count = models.IntegerField()
	favourites_count = models.IntegerField()
	friends_count = models.IntegerField()
	id_str = models.CharField(max_length=40)
	location = models.CharField(max_length=200)
	profile_image_url = models.URLField()
	updated_time = models.DateTimeField(auto_now=True)
	statuses_count = models.IntegerField()
	screen_name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.twittername.twittername

class OldTweet(models.Model):
	twittername = models.ForeignKey(TwitterAuth)
	text = models.CharField(max_length=200)
	created_at = models.DateTimeField()
	favorite_count = models.IntegerField()
	retweet_count = models.IntegerField()
	id_str = models.CharField(max_length=200)

	def __unicode__(self):
		return self.twittername.twittername

##########    FORMS   ############

class SettingForm(ModelForm):

	class Meta:
		model = Settings
		fields = ['paytier']


class TwitterAuthForm(forms.ModelForm):
	class Meta:
		model = TwitterAuth
		exclude = ['user']

	def __init__(self, *args, **kwargs):
		super(TwitterAuthForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-4'
		self.helper.field_class = 'col-lg-8'
		self.helper.layout = Layout(
		'twittername',
		'consumer_key',
		'consumer_secret',
		'access_token_key',
		'access_token_secret',
		    StrictButton('Add Twitter ', name='addtwitter', type='submit',css_class='btn-primary'),
		)

	def clean(self):
		cleaned_data = super(TwitterAuthForm, self).clean()
		consumer_key = str(cleaned_data.get('consumer_key'))
		consumer_secret = str(cleaned_data.get('consumer_secret'))
		access_token_key = str(cleaned_data.get('access_token_key'))
		access_token_secret = str(cleaned_data.get('access_token_secret'))

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token_key,access_token_secret)
		api = tweepy.API(auth)

		try: api.me()
		except tweepy.TweepError:
			raise forms.ValidationError('Twitter rejected your keys.  See the sidebar to resolve the issue.')

		return cleaned_data

class TwitterSearchForm(ModelForm):
	class Meta:
		model = TwitterSearch
		exclude = ['twittername']

	def __init__(self, *args, **kwargs):
		super(TwitterSearchForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.layout = Layout(
		'search',
		    StrictButton('Search Twitter', name='searchtwitter', type='submit',css_class='btn-primary'),
		    StrictButton('<span class="glyphicon glyphicon-floppy-disk"></span>', name='savesearch', type='submit',css_class='btn-default'),
		)

class TwitterScheduledForm(ModelForm):
	class Meta:
		model = TwitterScheduled
		exclude = ['twittername', 'created']

	def __init__(self, *args, **kwargs):
		super(TwitterScheduledForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.layout = Layout(
		'tweet',
		'time',
		    StrictButton('Schedule Tweet', name='scheduletweet', type='submit',css_class='btn-primary'),
		)

class TwitterCompetitorForm(ModelForm):
	class Meta:
		model = TwitterCompetitor
		exclude = ['twittername']

	def __init__(self,account,*args,**kwargs):
		self.account = account
		super(TwitterCompetitorForm, self).__init__(*args,**kwargs)
		self.fields['competitorhandle'].label = ""
		self.fields['competitorname'].label = ""
		self.helper= FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.layout = Layout(
		    Field('competitorname',placeholder="Name", title='Name'),
		    PrependedText('competitorhandle', '@', placeholder="Twitter Handle"),
		    StrictButton('Add Account', css_class='btn-primary'),
)

	def clean(self):
		cleaned_data = super(TwitterCompetitorForm, self).clean()
		competitorhandle = str(cleaned_data.get('competitorhandle'))

		if competitorhandle.startswith('@'): raise forms.ValidationError('Do not include the @ sign!')
		account = self.account
		
		auth = tweepy.OAuthHandler(account.consumer_key, account.consumer_secret)
		auth.set_access_token(account.access_token_key,account.access_token_secret)

		api = tweepy.API(auth)

		try: api.get_user(competitorhandle)
		except tweepy.TweepError:
			raise forms.ValidationError("Account either doesn't exist, or is private")

		return cleaned_data