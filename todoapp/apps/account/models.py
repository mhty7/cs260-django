from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	#fname = models.CharField(max_length=20,blank=True,null=False)
	#lname = models.CharField(max_length=20,blank=True,null=False)
	#mname = models.CharField(max_length=20,blank=True,null=False)


