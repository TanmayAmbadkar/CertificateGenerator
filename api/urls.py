from rest_framework.authtoken.views import obtain_auth_token  # <-- Here
from api.views import *
from django.urls import path

urlpatterns = [
        path('get', GetCertificates.as_view(),name = 'get_cert'),
        path('generate', UploadInfo.as_view(), name='generate_cert'),
        path('upload', UploadCertificates.as_view(), name='upload_cert'),
        path('login', LoginTokenView.as_view(), name='login_token'),
        path('logout', LogoutTokenView.as_view(), name='logout_token'),
        path('password-reset-email', RequestPasswordResetEmail.as_view(), name='password-reset-email'),
        path('reset-password', PasswordResetConfirm.as_view(), name='reset-password')
]
