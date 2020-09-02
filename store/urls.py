from django.urls import path
from backend.views import *
from django.conf.urls import include

urlpatterns = [

    path('home/', HomeView.as_view(), name = 'home'),
    path('upload/', uploadView, name = 'upload'),
    path('verify/', verifyView, name = 'verify'),
    path('not_found/', NotFoundView.as_view(), name = 'not_found'),
    path('found/', FoundView.as_view(), name = 'found'),

]
