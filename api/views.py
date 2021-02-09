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
from rest_framework.response import Response

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

    permission_classes = (IsAuthenticated,)
    def post(self, request):

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
        details = df.values
        response_list = {'columns': columns}
        response_list['cert'] = TempCertSerializer(cert).data
        for detail in details:

            response = {}
            for column, value in zip(columns, detail):

                response[column] = value

            response_list[detail[-5]] = response

        return JsonResponse(response_list)

class UploadCertificates(APIView):

    permission_classes=(IsAuthenticated,)

    def post(self, request):

        try:
            id = request.data.get("id")

            cert = TempCert.objects.get(id=id)
            zip = request.FILES['zip']
            df = pd.read_csv(csv)
            df.head()
            data = df[['RollNo', 'Certificate ID', 'Filename', 'Name', 'Date', 'Email']]

            processing(event, year, data, zip)
            scheduler = BackgroundScheduler()
            scheduler.add_job(func = mails, args = (data, event, year))
            scheduler.start()

            return JsonResponse(status=200, data={"message": "Process successful!"})

        except:
            return JsonResponse(status = 500, data={"Message:Some error occurred"})



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
