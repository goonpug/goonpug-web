from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()


# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Auth
    url(r'^logout/', 'django.contrib.auth.views.logout'),
    url(r'^', include('social_auth.urls')),
    url(r'^', include('apps.core.urls')),

    # generic
    url(r'^$', TemplateView.as_view(template_name='index.html')),
)
