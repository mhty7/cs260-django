from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from todoapp.apps.account.forms import UserAddForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

def user_login(request):
	if request.method == 'POST':
		username=request.POST.get('login_username')
		password=request.POST.get('login_username')
		next=request.POST.get('next','None')
		user=authenticate(username=username,password=password)

		if not User.objects.filter(username=username).exists() or user is None:
			messages.add_message(request,messages.WARNING,'failed to login.')
			return HttpResponseRedirect(reverse('index'))
		login(request,user)
		if next == 'None':
			return HttpResponseRedirect(reverse('index'))
		return HttpResponseRedirect(next)



def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def my_admin(request):
	if request.user.is_superuser:
		users=User.objects.all()

		if request.method=='POST':
			form=UserAddForm(request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(reverse('my_admin'))

		else:
			form=UserAddForm()
		return render(request,'account/myadmin.html',{'title':'my admin','form':form,'users':users})
	else:
		return HttpResponseRedirect(reverse('index'))


def delete_user(request,user_id):
	if request.user.is_superuser:
		try:
			user=User.objects.get(id=user_id)
		except ObjectDoesNotExist:
			raise Http404
		user.delete()
	return HttpResponseRedirect(reverse('my_admin',))
	



