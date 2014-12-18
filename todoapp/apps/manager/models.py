from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models import Q

class List(models.Model):
	user=models.ForeignKey(User,blank=True,null=True,related_name='list')

	def update_tasks_with_latest_date(self,latest_date):
		queryQ=Q()
		queryQ.add(Q(start_date__lt=latest_date) & Q(Q(canceled=False) & Q(completed=False)),Q.AND)
		tasks=self.tasks.filter(queryQ)

		for t in tasks:
			if t.start_date!=t.end_date:
				continue
			t.start_date=latest_date
			t.end_date=latest_date
			t.save()


	
class Task(models.Model):
	TYPE=(
		(1,'Every day'),
		(7,'Every week'),
		(30,'Every month'),
	)
	note = models.TextField(default='')
	list=models.ForeignKey(List,default=None,related_name='tasks',blank=True,null=True)

	freq=models.IntegerField(default=1,choices=TYPE)
	start_date=models.DateField()
	end_date=models.DateField()
	created_date=models.DateField()
	last_completed=models.DateField(blank=True, null=True)
	completed=models.BooleanField(default=False)
	canceled=models.BooleanField(default=False)


	def save(self,*args,**kwargs):
		if not self.id:
			now=date.today()
			self.start_date=now
			self.end_date=now
			self.created_date=now
			self.completed=False
			self.canceled=False
		if self.completed or self.canceled:
			self.last_completed=date.today()
		super(Task,self).save()




