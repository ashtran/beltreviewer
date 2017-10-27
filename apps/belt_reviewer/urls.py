from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),        #<--- render index.html
    url(r'^createuser$', views.createuser),     #<--- redirect /dashboard
    url(r'^login$', views.login),       #<--- redirect  /dashboard
    url(r'^dashboard$', views.dashboard),       #<--- render dashboard.html
    url(r'^addbook$', views.addbook),       #<--- render newbook.html
    url(r'^processbook$', views.processbook),   #<-- redirect /reviews/<book_id>
    url(r'^reviews/(?P<book_id>\d+)$', views.reviews),  #<--- render reviews.html
    url(r'^remove/(?P<book_id>\d+)$', views.delete), #<--- redirect
    url(r'^user/(?P<user_id>\d+)$', views.user),    #<--- render user.html
    url(r'^reviews/(?P<book_id>\d+)/add$', views.addreview),    #<---  redirect /review/<book_id>
    url(r'^logout$', views.logout)      #<---   redirect /
]
