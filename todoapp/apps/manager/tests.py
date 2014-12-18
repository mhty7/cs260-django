from django.test import TestCase,LiveServerTestCase
from selenium import webdriver
from todoapp.settings import LOGIN_URL
from todoapp.apps.manager.views import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse,resolve
from django.http import HttpRequest
import unittest
from todoapp.apps.manager.models import *
from django.template.loader import render_to_string
from datetime import date
from django.test.client import RequestFactory
import mock
from dateutil.relativedelta import relativedelta



class  FakeDate(date):
	def __new__(cls,*args,**kwargs):
		return date.__new__(date,*args,**kwargs)
		


class ChangeFormTest(TestCase):
	def test_emits_error_if_dates_are_not_in_chronological_order(self):
		today=date.today()
		tomorrow=today+relativedelta(days=1)
		recurring=True
		freq=1
		form = DateChangeForm(data={'start_date':tomorrow,'end_date':today,'recurring':recurring,'freq':freq})
		self.assertFalse(form.is_valid())

	def test_dates_ends_up_the_same_if_recurring_false(self):
		today=date.today()
		tomorrow=today+relativedelta(days=1)
		recurring=False
		freq=1
		form = DateChangeForm(data={'start_date':tomorrow,'end_date':today,'recurring':recurring,'freq':freq})
		self.assertTrue(form.is_valid())
		obj=form.save()
		self.assertTrue(obj.start_date==obj.end_date==today)

	def test_form_saves_the_model_object(self):
		today=date.today()
		tomorrow=today+relativedelta(days=1)
		recurring=False
		freq=1
		form = DateChangeForm(data={'start_date':tomorrow,'end_date':today,'recurring':recurring,'freq':freq})
		self.assertTrue(form.is_valid())
		obj=form.save()
		task=Task.objects.get(id=obj.id)
		self.assertTrue(obj.start_date==task.start_date)






class HomePageTest(TestCase):
	def setUp(self):
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)
		self.factory = RequestFactory()

	def tearDown(self):
		self.user.delete()
		self.admin.delete()

	def test_root_url_resolves_to_index_page_view(self):
		found=resolve('/')
		self.assertEqual(found.func,index)



	def test_index_page_only_saves_items_when_necessary_without_authenticated(self):
		request=self.factory.get('/')
		request.user = self.user
		request.user.is_authenticated=mock.Mock(return_value=False)
		index(request)
		self.assertEqual(Task.objects.count(),0)



	def test_forward_page_to_list_page_if_there_is_associated_list(self):
		list_=List()
		list_.user=self.user
		list_.save()
		request = self.factory.get('/')
		request.user = self.user
		request.user.is_authenticated=mock.Mock(return_value=True)
		response = index(request)
		self.assertEqual(response['location'],reverse('view_list',kwargs={'list_id':self.user.list.first().id}))



class UpdateTaskTest(TestCase):


	def test_cannot_change_without_being_authed(self):
		self.user= User.objects.create_user(username='user',email="",password='user',)
		list_=List.objects.create(user=self.user)
		task=Task.objects.create(note='something',list=list_)
		response=self.client.post('/lists/%d/update_task/' % (list_.id,),
			data={'form-0-id':task.id,'form-0-canceled':'on','form-0-completed':'on',
			'form-TOTAL_FORMS':1,'form-INITIAL_FORMS':1})
		self.assertEqual(response.status_code,404)

	def test_change_a_status_request(self):
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.client.login(username='user',password='user')
		list_=List.objects.create(user=self.user)
		task=Task.objects.create(note='something',list=list_)
		response=self.client.post('/lists/%d/update_task/' % (list_.id,),
			data={'form-0-id':task.id,'form-0-canceled':'on','form-0-completed':'on',
			'form-TOTAL_FORMS':1,'form-INITIAL_FORMS':1})
		task=Task.objects.get(id=task.id)
		self.assertEqual(task.canceled,True)
		self.assertEqual(task.completed,True)






class NewListTest(TestCase):
	def test_saving_a_post_request(self):
		self.client.post('/lists/new/',data={'item_text':'A new list item'})

		self.assertEqual(Task.objects.count(),1)
		new_task=Task.objects.first()
		self.assertEqual(new_task.note,'A new list item')

	def test_redirects_after_post(self):
		response=self.client.post(
			'/lists/new/',data={'item_text':'A new list item'},
		)
		new_list=List.objects.first()
		self.assertRedirects(response,'/lists/%d/' % (new_list.id,))

	def test_cannot_see_list_from_other_user(self):
		user1= User.objects.create_user(username='user1',email="",password='user1',)
		user2= User.objects.create_user(username='user2',email="",password='user2',)
		self.client.login(username="user2",password="user2")
		list_=List.objects.create(user=user1)
		task=Task.objects.create(note='something',list=list_)
		response=self.client.get('/lists/%d/' % (list_.id,))
		self.assertEqual(response.status_code,404)

	def test_cannot_see_list_from_anonymous(self):
		user1= User.objects.create_user(username='user1',email="",password='user1',)
		list_=List.objects.create(user=user1)
		task=Task.objects.create(note='something',list=list_)
		response=self.client.get('/lists/%d/' % (list_.id,))
		self.assertEqual(response.status_code,404)











class ListViewTest(TestCase):
	def setUp(self):
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)
		self.factory = RequestFactory()

	def tearDown(self):
		self.user.delete()
		self.admin.delete()

	def test_passes_correct_list_to_template(self):
		other_list=List.objects.create()
		correct_list=List.objects.create()
		response=self.client.get('/lists/%d/' % (correct_list.id))
		self.assertEqual(response.context['list'],correct_list)

	def test_uses_list_template(self):
		list_=List.objects.create()
		response=self.client.get('/lists/%d/' % (list_.id,))
		self.assertTemplateUsed(response,'manager/list.html')

	def test_displays_only_items_for_that_list(self):
		correct_list=List.objects.create()
		Task.objects.create(note='note 1',list=correct_list)
		Task.objects.create(note='note 2',list=correct_list)
		other_list=List.objects.create()
		Task.objects.create(note='other note 1',list=other_list)
		Task.objects.create(note='other note 2',list=other_list)

		response = self.client.get('/lists/%d/' % (correct_list.id))

		self.assertContains(response,'note 1')
		self.assertContains(response,'note 2')
		self.assertNotContains(response,'other note 1')
		self.assertNotContains(response,'other note 2')

	def test_displays_all_tasks(self):
		list_=List.objects.create()

		first_task=Task()
		first_task.note='The First list item'
		first_task.list=list_
		first_task.save()

		second_task=Task()
		second_task.note='The Second list item'
		second_task.list=list_
		second_task.save()

		response=self.client.get('/lists/%d/' % (list_.id,))
		#for byte code
		self.assertContains(response,'The First list item')
		self.assertContains(response,'The Second list item')

	def test_pass_currentdate_to_template(self):
		list_=List.objects.create()
		response=self.client.get('/lists/%d/' % (list_.id,))
		today=date.today()
		#date='%s/%s/%s' % (today.month,today.day,today.year)
		self.assertEqual(response.context['today'],today)

	def test_displays_only_items_undone_or_uncanceled_or_on_today(self):
		self.client.login(username='user',password='user')
		list_=List.objects.create(user=self.user)
		task1=Task.objects.create(note='note 1',list=list_)
		task2=Task.objects.create(note='note 2',list=list_)
		task3=Task.objects.create(note='note 3',list=list_)
		task4=Task.objects.create(note='note 4',list=list_)

		task1.completed=True
		task1.save()

		task2.canceled=True
		task2.save()

		task3.completed=True
		task3.canceled=True
		task3.save()

		response = self.client.get('/lists/%d/' % (list_.id))

		self.assertContains(response,'note 1')
		self.assertContains(response,'note 2')
		self.assertContains(response,'note 3')
		self.assertContains(response,'note 4')

		today=date.today()
		tomorrow=today+relativedelta(days=1)

		with mock.patch('todoapp.apps.manager.views.date',FakeDate):
			FakeDate.today=classmethod(lambda cls:tomorrow)
			response=self.client.get('/lists/%d/' % (list_.id))
			self.assertNotContains(response,'note 1')
			self.assertNotContains(response,'note 2')
			self.assertNotContains(response,'note 3')
			self.assertContains(response,'note 4')


	
	def test_displays_transfered_task_within_the_day_even_after_change(self):
		self.client.login(username='user',password='user')
		list_=List.objects.create(user=self.user)
		task1=Task.objects.create(note='hello world',list=list_)


		response = self.client.get('/lists/%d/' % (list_.id))

		self.assertContains(response,'hello world')


		today=date.today()
		tomorrow=today+relativedelta(days=1)
		daftert=tomorrow+relativedelta(days=1)
		with mock.patch('todoapp.apps.manager.models.date',FakeDate):
			with mock.patch('todoapp.apps.manager.views.date',FakeDate):
				FakeDate.today=classmethod(lambda cls:tomorrow)
				self.assertEqual(task1.start_date,today)
				self.assertEqual(task1.completed,False)
				self.assertEqual(task1.canceled,False)
				
				#the start_date and end_date will be updated with the latest time.
				response=self.client.get('/lists/%d/' % (list_.id))
				self.assertEqual(response.status_code,200)

				#re-get the object
				task1=Task.objects.get(id=task1.id)
				self.assertEqual(task1.start_date,tomorrow)

				task1.completed=True
				task1.save()

				response=self.client.get('/lists/%d/' % (list_.id))
				self.assertContains(response,'hello world')

				FakeDate.today=classmethod(lambda cls:daftert)
				response=self.client.get('/lists/%d/' % (list_.id))
				self.assertNotContains(response,'hello world')





class ListAndTaskModelsTest(TestCase):
	def setUp(self):
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)
		self.factory = RequestFactory()

	def tearDown(self):
		self.user.delete()
		self.admin.delete()

	def test_creates_task_and_shows_same_three_dates(self):
		task=Task()
		task.note='something'
		task.save()
		self.assertTrue(task.start_date==task.end_date==task.created_date)

	def test_shows_original_dates_even_after_changes(self):
		task=Task()
		task.note='something'
		task.save()
		task.note="something_else"
		task.save()
		self.assertFalse(task.note=='something')
		self.assertTrue(task.start_date==task.end_date==task.created_date)

	def test_be_able_to_toggle_switches(self):
		task=Task()
		task.note="something"
		task.save()
		self.assertTrue(task.completed==False and task.canceled==False)
		task.completed=True
		task.save()
		self.assertTrue(task.completed==True and task.canceled==False)
		task.canceled=True
		task.save()
		self.assertTrue(task.completed==True and task.canceled==True)

	#override date module in this test with FakeDate
	#otherwise ,normally they have own global name to refference
	def test_shows_the_latest_date_on_update(self):
		#needed if this module is also covered by FakeDate to obtain real date?
		#from datetime import date
		task=Task()
		task.note="something"
		task.save()
		today=date.today()
		tomorrow=today+relativedelta(days=1)
		daftert=tomorrow+relativedelta(days=1)

		with mock.patch('todoapp.apps.manager.models.date',FakeDate):
			FakeDate.today=classmethod(lambda cls:tomorrow)
			#mock_date.today.return_value=tomorrow
			#mock_date.side_effect=lambda *args, **kw: date(*args,**kw)
			task.completed=True
			task.save()
			self.assertEqual(task.start_date,today)
			self.assertEqual(task.last_completed,tomorrow)
			
			FakeDate.today=classmethod(lambda cls:daftert)
			task.canceled=True
			task.save()
			self.assertEqual(task.last_completed,daftert)





	def test_saving_with_user_and_retrieving_items(self):
		list_=List()
		list_.user=self.user
		list_.save()

		first_task=Task()
		first_task.note='The First list item'
		first_task.list=list_
		first_task.save()

		second_task=Task()
		second_task.note='The Second list item'
		second_task.list=list_
		second_task.save()

		saved_tasks=Task.objects.all()

		list_associated_user=self.user.list.first()

		self.assertEqual(list_,list_associated_user)
		self.assertTrue(list(saved_tasks),list(list_associated_user.tasks.all()))

	def test_saving_without_user(self):
		list_=List()
		list_.save()

		self.assertEqual(list_.user,None)



	def test_saving_and_retrieving_items(self):
		list_= List()
		list_.save()

		first_task=Task()
		first_task.note='The First list item'
		first_task.list=list_
		first_task.save()

		second_task=Task()
		second_task.note='The Second list item'
		second_task.list=list_
		second_task.save()

		saved_list=List.objects.first()
		self.assertEqual(saved_list,list_)

		saved_tasks=Task.objects.all()
		self.assertEqual(saved_tasks.count(),2)

		first_saved_task=saved_tasks[0]
		second_saved_task=saved_tasks[1]
		self.assertEqual(first_saved_task.note,'The First list item')
		self.assertEqual(first_saved_task.list,list_)
		self.assertEqual(second_saved_task.note,'The Second list item')
		self.assertEqual(second_saved_task.list,list_)





