from django.urls import path
from store.views import *
from django.conf.urls import include

urlpatterns = [

    path('home/', HomeView.as_view(), name = 'home'),
    path('upload/', uploadView, name = 'upload'),
    path('generate/', generate_certs, name = 'generate'),
    path('verify/', verifyView, name = 'verify'),
    path('not_found/', NotFoundView.as_view(), name = 'not_found'),
    path('certificate/<str:pk>', CertificateDetailView.as_view(), name='certificate'),
    path('count', CertficateCount.as_view(), name='count')

]
