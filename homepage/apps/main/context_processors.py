from django.conf import settings
from apps.main.models import TwitterAuth





def systemstarterkit(request): 
	try:
	    twitteraccts = TwitterAuth.objects.filter(user=request.user)
	    return {'twitteraccts':twitteraccts,}
	except:
		return {}
