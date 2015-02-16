from django.conf.urls import patterns, include, url

from django.contrib import admin

from smyt.core.views import IndexView, model_info, model_objects

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^model/(?P<model>\w+)/info/$', model_info, name='model_info'),
    url(r'^model/(?P<model>\w+)/$', model_objects, name='model_objects_get'),
    url(r'^model/(?P<model>\w+)/(?P<object_id>\d+)/$', model_objects, name='model_objects_post'),
    url(r'^admin/', include(admin.site.urls)),
)
