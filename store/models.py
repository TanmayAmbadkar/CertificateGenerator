from django.db import models

# Create your models here.

class Certificate(models.Model):

    cert_id = models.CharField(max_length = 200)
    rollno = models.CharField(max_length = 12)
    event = models.CharField(max_length = 20)
    year = models.CharField(max_length = 4)
    name = models.CharField(max_length=100, null = True)


    def __str__(self):
        return self.cert_id

'''
def file_path(instance):

    return f"certificates/{instance.event}/{instance.year}/"

class CertFile(models.Model):

    cert_id = models.CharField(max_length = 200)
    file = models.FileField(upload_to=file_path)
'''
