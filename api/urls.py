from rest_framework.authtoken.views import obtain_auth_token  # <-- Here
from api.views import *
from django.urls import path

urlpatterns = [
        path('get_cert', GetCertificates.as_view(),name = 'get_cert'),
        path('gen_cert', UploadInfo.as_view(), name='gen_cert'),
        path('up_cert', UploadCertificates.as_view(), name='up_cert'),
        path('login/', obtain_auth_token, name='auth_token'),
]
