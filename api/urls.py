from rest_framework.authtoken.views import obtain_auth_token  # <-- Here
from api.views import *
from django.urls import path

urlpatterns = [
        path('get', GetCertificates.as_view(),name = 'get_cert'),
        path('generate', UploadInfo.as_view(), name='generate_cert'),
        path('upload', UploadCertificates.as_view(), name='upload_cert'),
        path('login', obtain_auth_token, name='get_auth_token'),
]
