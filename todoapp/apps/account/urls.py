from django.conf.urls import patterns, include, url



urlpatterns = patterns('todoapp.apps.account.views',
    url(r'^login/$','user_login',name='login'),
    url(r'^logout/$','user_logout',name='logout'),
    url(r'^myadmin/$','my_admin',name='my_admin'),
    url(r'^myadmin/(?P<user_id>\d+)/delete/$','delete_user',{},name='delete_user'),

)
