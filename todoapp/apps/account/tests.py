from django.test import TestCase,LiveServerTestCase
from selenium import webdriver
from todoapp.settings import LOGIN_URL
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import unittest
from todoapp.apps.account.models import UserProfile
from django.contrib import auth

class AccountTest(TestCase):
	def setUp(self):
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)

	def tearDown(self):
		self.user.delete()
		self.admin.delete()


	def test_login(self):
		post_data = {'login_password':'user','login_username':'user','next':'/',}
		response = self.client.post(reverse('login'),data=post_data)
		self.assertRedirects(response,reverse('index'),status_code=302, target_status_code=302)
		user = auth.get_user(self.client)
		self.assertFalse(user.is_anonymous())

	def test_login_failure_shows_message(self):
		post_data = {'login_password':'wrong','login_username':'wrong','next':'/',}
		response = self.client.post(reverse('login'),data=post_data,follow=True)
		self.assertContains(response,'failed to login.',)

	def test_logout(self):
		response = self.client.get(reverse('logout'),follow=True)
		self.assertRedirects(response,reverse('index'))
		user=auth.get_user(self.client)
		self.assertTrue(user.is_anonymous())

	def test_uses_list_template(self):
		self.client.login(username='admin',password='admin')
		response=self.client.get('/user/myadmin/')
		self.assertTemplateUsed(response,'account/myadmin.html')
		self.client.logout()
		response=self.client.get('/user/myadmin/')
		self.assertRedirects(response,'/')

	def test_newly_added_user_returned(self):
		self.client.login(username='admin',password='admin')
		response=self.client.post('/user/myadmin/',
			data={'username':'mae','first_name':'maekun','email':'mae@gmail.com',
			'password1':'mae','password2':'mae'})
		user=User.objects.get(username='mae')
		self.assertEqual(user.first_name,'maekun')
		self.assertEqual(user.email,'mae@gmail.com')

	def test_fail_if_passwords_do_not_match(self):
		self.client.login(username='admin',password='admin')
		response=self.client.post('/user/myadmin/',
			data={'username':'mae','first_name':'maekun','email':'mae@gmail.com',
			'password1':'mae','password2':'wrong'})
		self.assertFalse(User.objects.filter(username='mae'))

	def test_failed_and_forwarded_without_being_auth(self):
		response=self.client.post('/user/myadmin/',
			data={'username':'mae','first_name':'maekun','email':'mae@gmail.com',
			'password1':'mae','password2':'mae'})
		self.assertRedirects(response,'/')



	def test_delete_user(self):
		self.client.login(username='admin',password='admin')
		self.assertTrue(User.objects.filter(username='user'))
		response=self.client.get(reverse('delete_user',kwargs={'user_id':self.user.id}))
		self.assertFalse(User.objects.filter(username='user'))






class AccountBrowserTest(LiveServerTestCase):
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)

	def tearDown(self):
		self.user.delete()
		self.admin.delete
		self.browser.quit()

	def test_can_access_admin_site(self):
		
		self.browser.get(self.live_server_url+'/admin/')
		body=self.browser.find_element_by_tag_name('body')
		self.assertIn('Administration',body.text)













