from django.conf.urls import patterns, include, url
from ansi import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ansiweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/', views.upload,),
    url(r'^delfile/', views.delfile,),
    url(r'^pushfile/', views.pushfile,),
    url(r'^pssh/', views.pssh,),
)
