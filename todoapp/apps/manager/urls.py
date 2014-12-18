from django.conf.urls import patterns, include, url



urlpatterns = patterns('todoapp.apps.manager.views',
    url(r'^$','index',name='index'),
    url(r'^lists/(?P<list_id>\d+)/$','view_list',name='view_list'),
    url(r'^lists/(?P<list_id>\d+)/add_task/$','add_task',name='add_task'),
    url(r'^lists/(?P<list_id>\d+)/update_task/$','update_task',name='update_task'),
    url(r'^lists/new/$','new_list',name='new_list'),
    url(r'^lists/(?P<list_id>\d+)/monthly/','monthly_view_list',name='monthly_view_list'),
    url(r'^lists/(?P<list_id>\d+)/weekly/','weekly_view_list',name='weekly_view_list'),
    url(r'^task/(?P<task_id>\d+)/date_change/','date_change',name='date_change'),

)
