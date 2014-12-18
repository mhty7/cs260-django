from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

admin.site.site_header="Administration"

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'todoapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'',include('todoapp.apps.manager.urls')),
    url(r'^user/',include('todoapp.apps.account.urls')),
)
