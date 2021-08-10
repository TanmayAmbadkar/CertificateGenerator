from django.db import models

# Create your models here.

class Certificate(models.Model):

    id = models.CharField(max_length = 200, primary_key = True)
    cert_id = models.CharField(max_length = 200)
    rollno = models.CharField(max_length = 12)
    event = models.CharField(max_length = 20)
    year = models.CharField(max_length = 4)
    name = models.CharField(max_length=100, null = True)
    file = models.FileField(upload_to="certificates/", null = True)
    date = models.CharField(max_length = 12, null = True)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.cert_id

class TempCert(models.Model):

    image = models.FileField(upload_to = "images/", null = True)
    csv = models.FileField(upload_to = "csv/", null = True)
    event = models.CharField(max_length = 255, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)

    def __str__(self):
        return f"{self.event} {self.year}"
