from django.shortcuts import render, redirect
from store.models import *
from store.forms import *
from django.http import HttpResponseRedirect
import pandas as pd
from django.views.generic import TemplateView, DetailView
from zipfile import ZipFile
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from store.send_email import *
from backend import settings
from apscheduler.schedulers.background import BackgroundScheduler

# Create your views here.


def uploadView(request):

    if request.method == 'POST':

        form = CertificateForm(request.POST, request.FILES)

        if form.is_valid():
            csv = form.cleaned_data['csv']
            event = form.cleaned_data['event']
            year = form.cleaned_data['year']
            zip = request.FILES['certificates']

            df = pd.read_csv(csv)
            df.head()
            data = df[['RollNo', 'Certificate ID', 'Filename', 'Name', 'Date', 'Email']]

            processing(event, year, data, zip)
            scheduler = BackgroundScheduler()
            scheduler.add_job(func = mails, args = (data, event, year))
            scheduler.start()
            #mails(data, event, year)

            return HttpResponseRedirect('/home/')

    else:
        form = CertificateForm()

    return render(request, 'upload.html', {'form': form})

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


class HomeView(TemplateView):

    template_name = 'home.html'

def verifyView(request):

    if request.method == 'POST':

        form = VerificationForm(request.POST)

        if form.is_valid():

            rollno = form.cleaned_data['ID']

            certificates = Certificate.objects.all().filter(rollno = rollno)
            if(len(certificates)!=0):
                return render(request, 'found.html', {'certificates':certificates})
            else:

                try:
                    certificate = Certificate.objects.get(cert_id = rollno)
                    return HttpResponseRedirect(f'/certificate/{certificate.id}')
                except:
                    return HttpResponseRedirect('/not_found/')


    else:
        form = VerificationForm()

    return render(request, 'verify.html', {'form': form})

class CertficateCount(APIView):

    def get(self, request, format=None):

        certificates = Certificate.objects.all()
        return Response({"count": len(certificates)})

class CertificateDetailView(DetailView):

    model = Certificate
    template_name = 'certificate.html'

class NotFoundView(TemplateView):

    template_name = 'not_found.html'
