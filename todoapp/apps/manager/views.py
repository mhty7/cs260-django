from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from todoapp.apps.manager.models import *
from todoapp.apps.manager.forms import *
from django.core.urlresolvers import reverse
from datetime import date
from datetime import datetime
from django.http import Http404
from django.forms.models import modelformset_factory
from django.db.models import Q,F
import calendar
from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string
import json
from django.core.exceptions import ObjectDoesNotExist


def perdelta(start,end,delta):
	cur=start
	while cur <= end:
		yield cur
		cur=cur+delta



def index(request):
	if request.user.is_authenticated():
		list_=request.user.list.first()
		if list_==None:
			list_=List.objects.create(user=request.user)
		return HttpResponseRedirect('/lists/%d/' % (list_.id,))
	return render(request,'manager/index.html',{'title':'home',})

def view_list(request,list_id):
	try:
		list_=List.objects.get(id=list_id)
	except ObjectDoesNotExist:
		raise Http404
	if list_.user!=None and list_.user!=request.user:
		raise Http404

	today=date.today()
	list_.update_tasks_with_latest_date(today)


	queryQ=Q()
	queryQ.add(Q(start_date=today),Q.AND)

	objs=[]
	for t in list_.tasks.filter(Q(end_date__gt=F('start_date')) & Q(Q(canceled=False) & Q(completed=False))):
		tmpd=perdelta(t.start_date,t.end_date,relativedelta(days=t.freq))
		if today in tmpd:
			objs.append(t)
	queryQ.add(Q(id__in=[c.id for c in objs]),Q.OR)
	tasks=list_.tasks.filter(queryQ).order_by('id')

	fset=modelformset_factory(Task,formset=MyModelFormsetBase,form=TaskCheckForm,extra=0)
	forms=fset(queryset=tasks)
	
	return render(request,'manager/daily_list.html',{'title':'view list','list':list_,'today':today,'forms':forms})


def monthly_view_list(request,list_id):
	try:
		list_=List.objects.get(id=list_id)
	except ObjectDoesNotExist:
		raise Http404
	if list_.user!=None and list_.user!=request.user:
		raise Http404

	today=date.today()
	cal=calendar.Calendar()
	days=cal.itermonthdays(today.year,today.month)
	output=[[]]
	week=0

	list_.update_tasks_with_latest_date(today)

	for day in days:
		tasks = current = False
		if day:

			d=date(today.year,today.month,day)

			queryQ=Q()
			queryQ.add(Q(start_date=d),Q.AND)

			objs=[]
			for t in list_.tasks.filter(Q(end_date__gt=F('start_date')) & Q(Q(canceled=False) & Q(completed=False))):
				tmpd=perdelta(t.start_date,t.end_date,relativedelta(days=t.freq))
				if d in tmpd:
					objs.append(t)
			queryQ.add(Q(id__in=[c.id for c in objs]),Q.OR)
			tasks=list_.tasks.filter(queryQ).order_by('id')



			if day==today.day:
				current=True
		output[week].append((day,tasks,current))
		if len(output[week])==7:
			output.append([])
			week=week+1

	return render(request,'manager/monthly_list.html',{'title':'view list','list':list_,'today':today,'output':output})




def weekly_view_list(request,list_id):
	try:
		list_=List.objects.get(id=list_id)
	except ObjectDoesNotExist:
		raise Http404
	if list_.user!=None and list_.user!=request.user:
		raise Http404

	today=date.today()
	theday=calendar.weekday(today.year,today.month,today.day)
	firstday=today-relativedelta(days=theday)

	output=[]
	list_.update_tasks_with_latest_date(today)

	for i in range(0,7):
		tasks=current=False
		delta=relativedelta(days=i)
		day=firstday+delta

		queryQ=Q()
		queryQ.add(Q(start_date=day),Q.AND)

		objs=[]
		for t in list_.tasks.filter(Q(end_date__gt=F('start_date')) & Q(Q(canceled=False) & Q(completed=False))):
			tmpd=perdelta(t.start_date,t.end_date,relativedelta(days=t.freq))
			if day in tmpd:
				objs.append(t)
		queryQ.add(Q(id__in=[c.id for c in objs]),Q.OR)
		tasks=list_.tasks.filter(queryQ).order_by('id')




		if day==today:
			current=True
		output.append((day,tasks,current))

	return render(request,'manager/weekly_list.html',{'title':'view list','list':list_,'today':today,'output':output})



def add_task(request,list_id):
	try:
		list_=List.objects.get(id=list_id)
	except ObjectDoesNotExist:
		raise Http404
	if list_.user!=None and list_.user!=request.user:
		raise Http404
	list_ = List.objects.get(id=list_id)
	new_item_text = request.POST['item_text']
	task=Task()
	task.note=new_item_text
	task.list=list_
	task.save()
	return HttpResponseRedirect('/lists/%d/' % (list_.id,))

def update_task(request,list_id):
	try:
		list_=List.objects.get(id=list_id)
	except ObjectDoesNotExist:
		raise Http404
	if list_.user!=None and list_.user!=request.user:
		raise Http404

	fset=modelformset_factory(Task,formset=MyModelFormsetBase,form=TaskCheckForm,extra=0)

	if request.method=='POST':
		forms=fset(request.POST)
		if forms.is_valid():
			for f in forms:
				f.save()
	return HttpResponseRedirect('/lists/%d/' % (list_.id,))

def new_list(request):
	list_=List.objects.create()
	new_item_text = request.POST['item_text']
	task=Task()
	task.note=new_item_text
	task.list=list_
	task.save()
	return HttpResponseRedirect('/lists/%d/' % (list_.id,))

def date_change(request,task_id):
	try:
		task_=Task.objects.get(id=task_id)
		list_=task_.list
	except ObjectDoesNotExist:
		raise Http404
	if list_.user!=None and list_.user!=request.user:
		raise Http404

	if request.method=="POST":
		form=DateChangeForm(request.POST,instance=task_)
		if form.is_valid():
			form.save()
			return HttpResponse(json.dumps("OK"))
		else:
			errors={}
			errors["non_field_errors"]="<br />".join(form.non_field_errors())
			return HttpResponseBadRequest(json.dumps(errors))
		
	else:
		form=DateChangeForm(instance=task_)
	return render(request,'manager/datepicker.html',{'form':form,})

