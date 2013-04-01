from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'Timekeeper.views.index', name='home'),
    url(r'^user/(?P<id>\d+)/$', 'Timekeeper.views.userpage'),
    url(r'^meetings/$', 'Timekeeper.views.meetings'),
    url(r'^api/user/(?P<id>\d+)/$', 'Timekeeper.api.user_api'),
    # url(r'^KUbe_tider/', include('KUbe_tider.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
