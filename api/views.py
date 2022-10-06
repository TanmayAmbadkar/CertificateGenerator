from ast import Pass
from multiprocessing import AuthenticationError
from tokenize import Token
from zipfile import ZipFile

from apscheduler.schedulers.background import BackgroundScheduler
from backend import settings
from django.conf import settings
from django.http import JsonResponse
from django.utils.encoding import (DjangoUnicodeDecodeError, force_str,
                                   smart_bytes)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from store.models import *
from store.serializers import *
from store.utils import *

from api.models import *
from api.serializer import (PasswordResetEmailSerializer,
                            SetNewPasswordSerializer)

# Create your views here.

class GetCertificates(APIView):

    def post(self, request):

        id = request.data.get("id")
        certificates = Certificate.objects.all().filter(rollno = id).order_by('id')
        if(len(certificates)!=0):
            return Response({'certificates':CertificateSerializer(certificates, many=True, context={'request': request}).data})
        else:

            try:
                certificate = Certificate.objects.get(cert_id = id)
                return Response({'certificate':CertificateSerializer(certificate, context={'request': request}).data})
            except:
                return Response(status=400, data={"message": "ID does not exist"})

        return Response(status=400, data={"message": "ID does not exist"})

class UploadInfo(APIView):

    def post(self, request):
        try:
            token = request.data.get('token')
            tok = LoginToken.objects.get(token=token)
        except LoginToken.DoesNotExist:
            return JsonResponse(status=403, data={"message":"access denied"})

        event = request.data.get("event")
        year = request.data.get("year")
        csv = request.data.get('csv')
        image = request.data.get('image')
        df = pd.read_csv(csv)
        certificate = Certificate.objects.order_by('-number').filter(year=year).first()
        try:
            number = certificate.number+1
        except:
            number = 1
        df = id_generate(df, number, year, event)
        cert = TempCert(image = image, event=event, year=year)
        cert.csv.name = f'csv/{event}_{year}.csv'
        cert.save()
        columns = df.columns.tolist()
        columns = columns[:-3]
        columns.append("Filename")
        details = df[columns].values
        response_list = {}
        response_list['cert'] = TempCertSerializer(cert).data
        for detail in details:
            response = {}
            for column, value in zip(columns, detail):

                if column == 'Email':
                    continue
                response[column] = value

            response_list[detail[-3]] = response

        columns = columns[:-1]
        response_list['columns'] = columns
        return JsonResponse(response_list)

class UploadCertificates(APIView):

    def post(self, request):
        try:
            token = request.data.get('token')
            tok = LoginToken.objects.get(token=token)
            if not tok.is_valid():
                return JsonResponse(status=403, data={"message":"access denied"})
        except LoginToken.DoesNotExist:
            return JsonResponse(status=403, data={"message":"access denied"})

        id = request.data.get("id")

        cert = TempCert.objects.get(id=id)
        zip = request.FILES['zip']
        df = pd.read_csv(cert.csv)
        df.head()
        data = df[['RollNo', 'Certificate ID', 'Filename', 'Name', 'Date', 'Email', 'Number']]

        processing(cert.event, cert.year, data, zip)

        scheduler = BackgroundScheduler()
        scheduler.add_job(func = mails, args = (data, cert.event, cert.year))
        scheduler.start()

        return JsonResponse(status=200, data={"message": "Process successful!"})




def mails(data, event, year):
    for i in range(len(data)):

        params = {
            'name': data['Name'][i],
            'email': data['Email'][i],
            'event': event,
            'year': year,
            'id': data['Certificate ID'][i].replace('-','_').replace('/','-')
        }

        send_mail(params, settings.EMAIL, settings.PASSWORD)


def processing(event, year, data, zip):
    with ZipFile(zip, 'r') as zipObj:
        zipObj.extractall('../media/certificates/')

    for i in range(len(data)):
        fname = f'certificates/{data["Filename"][i]}'

        obj = Certificate(
            cert_id = data['Certificate ID'][i],
            id = data['Certificate ID'][i],
            rollno = None if 'RollNo' not in data else data['RollNo'][i],
            event = event,
            year = year,
            name = data['Name'][i],
            date = data['Date'][i],
            number = data['Number'][i],
            institute_name = "IIITV" if 'Institute Name' not in data else data["Institute Name"][i],
            file = fname
        )
        obj.save()

class LoginTokenView(APIView):

    def post(self, request):

        username=request.data.get('username')
        password=request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):

                token = LoginToken(user = user)
                token.save()
                date = token.expiry
                year = date.year
                month = date.strftime("%B")
                day = date.day
                date = f"{month} {day}, {year} {date.strftime('%H:%M:%S')}"

                return JsonResponse(status=200, data={"token":token.token, "expiry":date})
            else:
                return JsonResponse(status=400, data={"message":"invalid username"})
        except User.DoesNotExist:
            return JsonResponse(status=400, data={"message":"invalid password"})

class LogoutTokenView(APIView):

    def post(self, request):

        token = request.data.get('token')
        try:
            tok = LoginToken.objects.get(token=token)
            tok.delete()
            return JsonResponse(status=200, data={"message":"successful"})
        except  LoginToken.DoesNotExist:
            return JsonResponse(status=400, data={"message":"does not exist"})

class RequestPasswordResetEmail(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PasswordResetEmailSerializer(data = request.data)

        if not serializer.is_valid():
            return Response(serializer.error_messages)

        email = serializer.validated_data.get("email")

        try:
            user = User.objects.get(email = email)
            if not user.is_superuser:
                return Response(
                    {
                        "error": "Access Denied"
                    },
                    status = status.HTTP_401_UNAUTHORIZED 
                )

            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetToken(user = user)
            token.save()

            password_reset_link = (
                "https://mycertificatesgymkhana.iiitvadodara.ac.in/reset-password/"
                + uidb64
                +"/"
                + token.token
                + "/"
            )

            params = {
                "name": user.first_name + user.last_name,
                "email": user.email,
                "link": password_reset_link
            }

            send_password_reset_mail(params, settings.EMAIL, settings.PASSWORD)

            return Response(
                {
                    "success": "Password reset link sent to your email, check your inbox"
                },
                status = status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {
                    "error": "No admin registered with this email id"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(e)

class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]

    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.error_messages)

        uidb64 = serializer.validated_data.get("uidb64")
        received_token = serializer.validated_data.get("token")

        user_id = force_str(urlsafe_base64_decode(uidb64))

        try:
            user = User.objects.get(id = user_id)
        except User.DoesNotExist:
            return Response(
                {
                    "error": "Invalid password reset link"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user_token = PasswordResetToken.objects.filter(user=user).values_list('token', flat=True)

        if received_token not in user_token:
            return Response(
                {
                    "error": "Invalid password reset link"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        password1 = serializer.data.get("password1")
        password2 = serializer.data.get("password2")

        if password1 != password2:
            return Response(
                {"error": "The two passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(password1)
        user.save()

        PasswordResetToken.objects.filter(token = received_token).delete()

        return Response(
            {
                "success": "Password reset successfull"
            },
            status=status.HTTP_200_OK
        )
