from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^create$', views.create),
    url(r'^login$', views.login),
    url(r'^dashboard$', views.dashboard),
    url(r'^addbook$', views.addbook),
    url(r'^processbook$', views.processbook),
    url(r'^reviews/(?P<book_id>\d+)$', views.reviews),
    url(r'^user/(?P<user_id>\d+)$', views.user),
]
