from django.shortcuts import render, redirect
from store.models import *
from store.forms import *
from django.http import HttpResponseRedirect
import pandas as pd
from django.views.generic import TemplateView
from zipfile import ZipFile
import os
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
            data = df[['RollNo', 'Certificate ID', 'Filename', 'Name', 'Date']]

            processing(event, year, data, zip)

            return HttpResponseRedirect('/home/')

    else:
        form = CertificateForm()

    return render(request, 'upload.html', {'form': form})


def processing(event, year, data, zip):

    with ZipFile(zip, 'r') as zipObj:
        zipObj.extractall('/home/ubuntu/CertificateGenerator/media/certificates/')

    for i in range(len(data)):
        fname = f'certificates/{data["Filename"][i]}'

        obj = Certificate(cert_id = data['Certificate ID'][i],
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

            id = form.cleaned_data['id']

            try:
                print('found!')
                certificate = Certificate.objects.get(cert_id=id)
                dict = {'name': certificate.name,
                        'rollno': certificate.rollno,
                        'id': certificate.cert_id,
                        'event': certificate.event,
                        'year': certificate.year,
                        'file': certificate.file,
			'date':certificate.date
		}

                return render(request, 'found.html', dict)
            except:
                print('Not found!')
                return HttpResponseRedirect('/not_found/')


    else:
        form = VerificationForm()

    return render(request, 'verify.html', {'form': form})

class NotFoundView(TemplateView):

    template_name = 'not_found.html'

class FoundView(TemplateView):

    template_name = 'found.html'
