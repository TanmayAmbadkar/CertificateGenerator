from django.shortcuts import render
from store.models import *
from store.forms import *
from django.http import HttpResponseRedirect
import pandas as pd
from django.views.generic import TemplateView


# Create your views here.


def uploadView(request):

    if request.method == 'POST':

        form = CertificateForm(request.POST)

        if form.is_valid():
            csv = form.cleaned_data['csv']

            df = pd.read_csv(csv)
            data = df[['RollNo', 'Hash', 'Filename']]

            processing(data)

            return HttpResponseRedirect('/home/')

    else:
        form = CertificateForm()

    return render(request, 'upload.html', {'form': form})

class HomeView(TemplateView):

    template_name = 'home.html'

def verifyView(request):

    if request.method == 'POST':

        form = VerificationForm(request.POST)

        if form.is_valid():

            id = form.cleaned_data['id']
            certificate = Certificate.objects.get(cert_id=id).first()

            if certificate is None:
                return HttpResponseRedirect('/found/')
            else:
                HttpResponseRedirect('/not_found/')


    else:
        form = VerificationForm()

    return render(request, 'verify.html', {'form': form})

class NotFoundView(TemplateView):

    template_name = 'not_found.html'

class FoundView(TemplateView):

    template_name = 'found.html'
