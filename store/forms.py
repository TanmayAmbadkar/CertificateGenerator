from django import forms
from store.models import *

class CertificateForm(forms.Form):

    event = forms.CharField(max_length=20)
    year = forms.CharField(max_length = 4)
    csv = forms.FileField()
    certificates = forms.FileField()

class VerificationForm(forms.Form):

    rollno = forms.CharField(max_length = 200)
