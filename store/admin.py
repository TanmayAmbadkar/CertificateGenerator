from django.contrib import admin
from store.models import *
# Register your models here.

class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "cert_id",
        "rollno",
        "event",
        "date",
        "year"
    )

    search_fields = ("rollno", "event", "cert_id", "year")

admin.site.register(Certificate, CertificateAdmin)
admin.site.register(TempCert)
