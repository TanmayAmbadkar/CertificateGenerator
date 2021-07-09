from django.shortcuts import render
from store.models import *
from rest_framework.utils import json
from rest_framework.views import APIView
from django.http import JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from backend import settings
from rest_framework.permissions import IsAuthenticated
from store.utils import *
from store.serializers import *
from store.models import *
from api.models import *
from rest_framework.response import Response
from zipfile import ZipFile
# Create your views here.

class GetCertificates(APIView):

    def post(self, request):

        id = request.data.get("id")
        print(id)
        certificates = Certificate.objects.all().filter(rollno = id).order_by('id')
        if(len(certificates)!=0):
            print("found rollno")
            return Response({'certificates':CertificateSerializer(certificates, many=True).data})
        else:

            try:
                certificate = Certificate.objects.get(cert_id = id)
                print("found cert")
                return Response({'certificate':CertificateSerializer(certificate).data})
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
        certificates = Certificate.objects.all()
        len(certificates)
        df = id_generate(df, len(certificates)+1, year, event)

        cert = TempCert(image = image, event=event, year=year)
        cert.csv.name = f'csv/{event}_{year}.csv'
        cert.save()
        columns = df.columns.tolist()
        columns = columns[:-3]
        details = df.values
        response_list = {'columns': columns}
        response_list['cert'] = TempCertSerializer(cert).data
        for detail in details:

            response = {}
            for column, value in zip(columns, detail):

                if column == 'RollNo' or column == 'Filename' or column == 'Email':
                    continue
                response[column] = value

            response_list[detail[-5]] = response

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
        data = df[['RollNo', 'Certificate ID', 'Filename', 'Name', 'Date', 'Email']]

        processing(cert.event, cert.year, data, zip)
        scheduler = BackgroundScheduler()
        scheduler.add_job(func = mails, args = (data, cert.event, cert.year))
        scheduler.start()

        return JsonResponse(status=200, data={"message": "Process successful!"})




def mails(data, event, year):
    for i in range(len(data)):

        params = {'name': data['Name'][i],
                  'email': data['Email'][i],
                  'event': event,
                  'year': year,
                  'id': data['Certificate ID'][i].replace('/','-')}

        send_mail(params, settings.EMAIL, settings.PASSWORD)


def processing(event, year, data, zip):

    with ZipFile(zip, 'r') as zipObj:
        zipObj.extractall('/home/ubuntu/CertificateGenerator/media/certificates/')

    for i in range(len(data)):
        fname = f'certificates/{data["Filename"][i]}'

        obj = Certificate(cert_id = data['Certificate ID'][i],
			  id = data['Certificate ID'][i].replace('/','-'),
                          rollno = data['RollNo'][i],
                          event = event,
                          year = year,
                          name = data['Name'][i],
			  date = data['Date'][i],
                          file = fname)
        obj.save()

class LoginTokenView(APIView):

    def post(self, request):

        username=request.data.get('username')
        password=request.data.get('password')
        print(username)
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
                print("Wrong pass")
                return JsonResponse(status=400, data={"message":"invalid username"})
        except User.DoesNotExist:
            print("Wrong username")
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
