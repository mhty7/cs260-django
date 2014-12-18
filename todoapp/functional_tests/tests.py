from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

import unittest
from selenium.webdriver.common.keys import Keys
import time
from datetime import date
from django.contrib.auth.models import User
import mock
from dateutil.relativedelta import relativedelta


class  FakeDate(date):
	def __new__(cls,*args,**kwargs):
		return date.__new__(date,*args,**kwargs)
		

class UserDifferentCalendaryViewTest(LiveServerTestCase):
	def setUp(self):
		self.browser=webdriver.Firefox()
		self.browser.implicitly_wait(10)
		self.user=User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)
	
	def tearDown(self):
		self.user.delete()
		self.admin.delete()
		self.browser.quit()


	def check_for_row_in_list_table(self,row_text):
		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		self.assertTrue(any( row_text in row.text for row in rows))


	def test_user_be_able_to_see_tasks_in_three_views(self):
		
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)


		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')

		userpanel=self.browser.find_element_by_css_selector('ul.user-panel')
		self.assertIn('User name: user',userpanel.text)

		inputbox=self.browser.find_element_by_id('id_new_item')
		self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
		inputbox.send_keys('Submit code for CS260')
		inputbox.send_keys(Keys.ENTER)
		

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')
		self.check_for_row_in_list_table('Submit code for CS260')

		time_text=self.browser.find_element_by_css_selector('h2.title').text
		today=date.today()
		self.assertIn('%s/%s/%s' % (today.month,today.day,today.year),time_text)



		tab_ul=self.browser.find_element_by_id('view_tab')
		lis=tab_ul.find_elements_by_tag_name('li')
		weeklybtn=lis[1].find_element_by_tag_name('a')


		weeklybtn.click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+/weekly/')
		task=self.browser.find_element_by_css_selector('table#id_list_table tr td.current')
		self.assertIn('Submit code for CS260',task.text)
		
		tab_ul=self.browser.find_element_by_id('view_tab')
		lis=tab_ul.find_elements_by_tag_name('li')
		monthlybtn=lis[2].find_element_by_tag_name('a')


		monthlybtn.click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+/monthly/')
		task=self.browser.find_element_by_css_selector('table#id_list_table tr td.current')
		self.assertIn('Submit code for CS260',task.text)




class AdminPageTest(LiveServerTestCase):
	def setUp(self):
		self.browser=webdriver.Firefox()
		self.browser.implicitly_wait(10)
		self.user=User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)

	def tearDown(self):
		self.user.delete()
		self.admin.delete()
		self.browser.quit()



	def test_superuser_goto_admin_page(self):
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)


		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')

		userpanel=self.browser.find_element_by_css_selector('ul.user-panel')

		lists=userpanel.find_elements_by_tag_name('li')
		self.assertIn('User name: user',lists[0].text)
		self.assertNotIn('Admin',userpanel.text)

		logout=self.browser.find_element_by_id('id_logout').click()

		self.browser.quit()
		self.browser=webdriver.Firefox()

		self.browser.get(self.live_server_url)




		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)


		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('admin')
		passwordinput.send_keys('admin')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')

		userpanel=self.browser.find_element_by_css_selector('ul.user-panel')

		lists=userpanel.find_elements_by_tag_name('li')
		self.assertIn('User name: admin',lists[0].text)
		self.assertIn('Admin',userpanel.text)


		self.browser.find_element_by_id('id_admin').click()
		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/user/myadmin/')

		title_text = self.browser.find_element_by_css_selector('h2').text
		self.assertIn('Add new user',title_text)

		add_form = self.browser.find_element_by_id('add_user')
		input_for_username=self.browser.find_element_by_id('id_username')
		input_for_fullname=self.browser.find_element_by_id('id_first_name')
		input_for_email = self.browser.find_element_by_id('id_email')
		input_for_password1=self.browser.find_element_by_id('id_password1')
		input_for_password2=self.browser.find_element_by_id('id_password2')

		input_for_username.send_keys('mae')
		input_for_fullname.send_keys('maekun')
		input_for_email.send_keys('mae@gmail.com')
		input_for_password1.send_keys('mae')
		input_for_password2.send_keys('mae')

		add_form.find_element_by_xpath('//input[@type="submit"]').click()

		current_url=self.browser.current_url
		self.assertRegex(current_url,'/user/myadmin/')


		data={'username':'mae','fullname':'maekun','email':'mae@gmail.com',}
		user_list=self.browser.find_element_by_id('user_list')
		rows=user_list.find_elements_by_tag_name('tr')
		self.assertTrue( any(self.check_for_row_in_table(rows[i],data) for i in range(1,len(rows)) ))

		







	def check_for_row_in_table(self,row,data):
		tds=row.find_elements_by_tag_name('td')
		return tds[0].text==data['username'] and tds[1].text==data['fullname'] and tds[2].text==data['email']




class VisitorTestOnDifferentDay(LiveServerTestCase):
	def setUp(self):
		self.browser=webdriver.Firefox()
		self.browser.implicitly_wait(10)
		self.user=User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)

	def tearDown(self):
		self.user.delete()
		self.admin.delete()
		self.browser.quit()


	def check_for_row_in_list_table(self,row_text):
		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		self.assertTrue(any( row_text in row.text for row in rows))

	def check_for_row_not_in_list_table(self,row_text):
		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		self.assertFalse(any( row_text in row.text for row in rows))


	def test_see_tasks_undone_on_another_day(self):
		today=date.today()
		tomorrow=today+relativedelta(days=1)
		daftert=tomorrow+relativedelta(days=1)
		
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)


		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')

		userpanel=self.browser.find_element_by_css_selector('ul.user-panel')
		self.assertIn('User name: user',userpanel.text)

		inputbox=self.browser.find_element_by_id('id_new_item')
		self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
		inputbox.send_keys('Submit code for CS260')
		inputbox.send_keys(Keys.ENTER)
		

		inputbox=self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Go buy eggs to Savemore')
		inputbox.send_keys(Keys.ENTER)

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')
		self.check_for_row_in_list_table('Submit code for CS260')
		self.check_for_row_in_list_table('Go buy eggs to Savemore')

		time_text=self.browser.find_element_by_css_selector('h2.title').text
		today=date.today()
		self.assertIn('%s/%s/%s' % (today.month,today.day,today.year),time_text)



		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		done_b=rows[1].find_element_by_name('form-0-completed')


		done_b.click()
		

		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		done_b=rows[1].find_element_by_name('form-0-completed')
		cancel_b=rows[1].find_element_by_name('form-0-canceled')

		

		self.assertFalse(cancel_b.is_selected())
		self.assertTrue(done_b.is_selected())

		self.browser.quit()
		self.browser=webdriver.Firefox()

		with mock.patch('todoapp.apps.manager.models.date',FakeDate):
			with mock.patch('todoapp.apps.manager.views.date',FakeDate):

				FakeDate.today=classmethod(lambda cls:tomorrow)
				self.browser.get(self.live_server_url)
				self.assertIn('To-Do',self.browser.title)
				header_text = self.browser.find_element_by_tag_name('h1').text
				self.assertIn('To-Do',header_text)

				loginform=self.browser.find_element_by_id('id_login_form')
				usernameinput=loginform.find_element_by_name('login_username')
				self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
				passwordinput=loginform.find_element_by_name('login_password')
				self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
				usernameinput.send_keys('user')
				passwordinput.send_keys('user')
				loginform.find_element_by_xpath('//input[@type="submit"]').click()

				list_url_1 = self.browser.current_url
				self.assertRegex(list_url_1,'/lists/.+')

				userpanel=self.browser.find_element_by_css_selector('ul.user-panel')
				self.assertIn('User name: user',userpanel.text)

				time_text=self.browser.find_element_by_css_selector('h2.title').text
				self.assertIn('%s/%s/%s' % (tomorrow.month,tomorrow.day,tomorrow.year),time_text)

				self.check_for_row_not_in_list_table('Submit code for CS260')
				self.check_for_row_in_list_table('Go buy eggs to Savemore')


				table=self.browser.find_element_by_id('id_list_table')
				rows=table.find_elements_by_tag_name('tr')
				done_b=rows[1].find_element_by_name('form-0-completed')


				done_b.click()
		

				table=self.browser.find_element_by_id('id_list_table')
				rows=table.find_elements_by_tag_name('tr')
				done_b=rows[1].find_element_by_name('form-0-completed')
				cancel_b=rows[1].find_element_by_name('form-0-canceled')

				self.assertFalse(cancel_b.is_selected())
				self.assertTrue(done_b.is_selected())

				self.browser.quit()
				self.browser=webdriver.Firefox()

				FakeDate.today=classmethod(lambda cls:daftert)
				self.browser.get(self.live_server_url)
				self.assertIn('To-Do',self.browser.title)
				header_text = self.browser.find_element_by_tag_name('h1').text
				self.assertIn('To-Do',header_text)


				loginform=self.browser.find_element_by_id('id_login_form')
				usernameinput=loginform.find_element_by_name('login_username')
				self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
				passwordinput=loginform.find_element_by_name('login_password')
				self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
				usernameinput.send_keys('user')
				passwordinput.send_keys('user')
				loginform.find_element_by_xpath('//input[@type="submit"]').click()

				list_url_1 = self.browser.current_url
				self.assertRegex(list_url_1,'/lists/.+')

				userpanel=self.browser.find_element_by_css_selector('ul.user-panel')
				self.assertIn('User name: user',userpanel.text)

				time_text=self.browser.find_element_by_css_selector('h2.title').text
				self.assertIn('%s/%s/%s' % (daftert.month,daftert.day,daftert.year),time_text)

				body_text = self.browser.find_element_by_tag_name('body').text
				self.assertIn('You are all done, today!',body_text)
			

			




		


	def test_time_mocking(self):
		today=date.today()
		tomorrow=today+relativedelta(days=1)

		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)



		inputbox=self.browser.find_element_by_id('id_new_item')
		self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
		inputbox.send_keys('Submit code for CS260')
		inputbox.send_keys(Keys.ENTER)
		
		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')
		self.check_for_row_in_list_table('Submit code for CS260')


		time_text=self.browser.find_element_by_css_selector('h2.title').text
		self.assertIn('%s/%s/%s' % (today.month,today.day,today.year),time_text)

		self.browser.quit()
		self.browser=webdriver.Firefox()

		


		with mock.patch('todoapp.apps.manager.views.date',FakeDate):
			FakeDate.today=classmethod(lambda cls:tomorrow)
			self.browser.get(self.live_server_url)
			self.assertIn('To-Do',self.browser.title)
			header_text = self.browser.find_element_by_tag_name('h1').text
			self.assertIn('To-Do',header_text)



			inputbox=self.browser.find_element_by_id('id_new_item')
			self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
			inputbox.send_keys('Submit code for CS260')
			inputbox.send_keys(Keys.ENTER)
		
			list_url_1 = self.browser.current_url
			self.assertRegex(list_url_1,'/lists/.+')
			self.check_for_row_in_list_table('Submit code for CS260')


			time_text=self.browser.find_element_by_css_selector('h2.title').text
			self.assertIn('%s/%s/%s' % (tomorrow.month,tomorrow.day,tomorrow.year),time_text)


class NewVisitorTest(LiveServerTestCase):
	def setUp(self):
		self.browser=webdriver.Firefox()
		self.browser.implicitly_wait(10)
		self.user= User.objects.create_user(username='user',email="",password='user',)
		self.admin=User.objects.create_superuser(username='admin',email="",password='admin',)


	def tearDown(self):
		self.user.delete()
		self.admin.delete()
		self.browser.quit()

	def wait_for(self,function_with_assertion,timeout=10):
		start_time=time.time()
		while time.time()-start_time<timeout:
			try:
				return function_with_assertion()
			except WebDriverException:
				time.sleep(0.1)
		return function_with_assertion()

	def check_for_row_in_list_table(self,row_text):
		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		self.assertTrue(any( row_text in row.text for row in rows))

	def test_can_tick_off_todo_and_confim_it_later(self):
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)


		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')

		userpanel=self.browser.find_element_by_css_selector('ul.user-panel')
		self.assertIn('User name: user',userpanel.text)

		inputbox=self.browser.find_element_by_id('id_new_item')
		self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
		inputbox.send_keys('Submit code for CS260')
		inputbox.send_keys(Keys.ENTER)
		self.check_for_row_in_list_table('Submit code for CS260')
		

		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		cancel_b=rows[1].find_element_by_name('form-0-canceled')

		#first_url=self.browser.current_url
		cancel_b.click()
		#self.wait_for(lambda: self.assertEqual(self.browser.current_url, first_url))


		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		done_b=rows[1].find_element_by_name('form-0-completed')


		done_b.click()

		#self.wait_for(lambda: self.assertEqual(self.browser.current_url, first_url))
		

		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		done_b=rows[1].find_element_by_name('form-0-completed')
		cancel_b=rows[1].find_element_by_name('form-0-canceled')

		

		self.assertTrue(cancel_b.is_selected())
		self.assertTrue(done_b.is_selected())

		logout=self.browser.find_element_by_id('id_logout').click()

		self.browser.quit()
		self.browser=webdriver.Firefox()

		self.browser.get(self.live_server_url)

		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_2 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')
		self.assertEqual(list_url_1,list_url_2)

		table=self.browser.find_element_by_id('id_list_table')
		rows=table.find_elements_by_tag_name('tr')
		cancel_b=rows[1].find_element_by_name('form-0-canceled')
		done_b=rows[1].find_element_by_name('form-0-completed')


		self.assertTrue(cancel_b.is_selected())
		self.assertTrue(done_b.is_selected())







	def test_can_login_and_see_his_todo_list(self):
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)


		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')

		userpanel=self.browser.find_element_by_css_selector('ul.user-panel')
		self.assertIn('User name: user',userpanel.text)

		inputbox=self.browser.find_element_by_id('id_new_item')
		self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
		inputbox.send_keys('Submit code for CS260')
		inputbox.send_keys(Keys.ENTER)
		self.check_for_row_in_list_table('Submit code for CS260')
		logout=self.browser.find_element_by_id('id_logout').click()

		self.browser.quit()
		self.browser=webdriver.Firefox()

		self.browser.get(self.live_server_url)

		loginform=self.browser.find_element_by_id('id_login_form')
		usernameinput=loginform.find_element_by_name('login_username')
		self.assertEqual(usernameinput.get_attribute('placeholder'),'username')
		passwordinput=loginform.find_element_by_name('login_password')
		self.assertEqual(passwordinput.get_attribute('placeholder'),'password')
		usernameinput.send_keys('user')
		passwordinput.send_keys('user')
		loginform.find_element_by_xpath('//input[@type="submit"]').click()

		list_url_2 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')
		self.assertEqual(list_url_1,list_url_2)

		self.check_for_row_in_list_table('Submit code for CS260')




		



	def test_can_start_a_list_and_retrieve_it_later(self):
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do',header_text)

		

		inputbox=self.browser.find_element_by_id('id_new_item')
		self.assertEqual(inputbox.get_attribute('placeholder'),'Enter your To-Do')
		inputbox.send_keys('Submit code for CS260')
		inputbox.send_keys(Keys.ENTER)
		
		list_url_1 = self.browser.current_url
		self.assertRegex(list_url_1,'/lists/.+')
		self.check_for_row_in_list_table('Submit code for CS260')

		time_text=self.browser.find_element_by_css_selector('h2.title').text
		today=date.today()
		self.assertIn('%s/%s/%s' % (today.month,today.day,today.year),time_text)



		inputbox=self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Go buy eggs to Savemore')
		inputbox.send_keys(Keys.ENTER)
		self.check_for_row_in_list_table('Submit code for CS260')
		self.check_for_row_in_list_table('Go buy eggs to Savemore')


		self.browser.quit()
		self.browser=webdriver.Firefox()

		self.browser.get(self.live_server_url)
		page_text=self.browser.find_element_by_tag_name('body').text
		self.assertNotIn('Submit code for CS260',page_text)
		self.assertNotIn('Go buy eggs to Savemore',page_text)

		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Go buy chocolates')
		inputbox.send_keys(Keys.ENTER)

		list_url_2=self.browser.current_url
		self.assertRegex(list_url_2,'/lists/.+')
		self.assertNotEqual(list_url_2,list_url_1)

		page_text=self.browser.find_element_by_tag_name('body').text
		self.assertNotIn('Go buy eggs to Savemore',page_text)
		self.assertIn('Go buy chocolates',page_text)

		


if __name__ == '__main__':
	unittest.main(warnings='ignore')