from django.db import models

# Create your models here.

class Certificate(models.Model):

    cert_id = models.CharField(max_length = 200)
    rollno = models.CharField(max_length = 12)
    event = models.CharField(max_length = 20)
    year = models.CharField(max_length = 4)
    cert = models.FileField(upload_to=f'{event}/{year}/')


    def __str__(self):
        return self.cert_id
