from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^fingerprints/$', views.FingerprintList.as_view()),
    url(r'^fingerprints/(?P<pk>[0-9]+)/$', views.FingerprintDetail.as_view()),
    url(r'^location/$', views.LocationEstimate.as_view()),
    url(r'^dedicated-groups/$', views.DedicatedGroupList.as_view()),
    url(r'^dedicated-groups/(?P<pk>[0-9]+)/$', views.DedicatedGroupDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
