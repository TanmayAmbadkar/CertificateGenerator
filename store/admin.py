from django.contrib import admin
from store.models import *
# Register your models here.

class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "Cert id",
        "Rollno",
        "Event",
        "Date",
        "Year"
    )

    search_fields = ("Rollno", "Event", "Cert id", "Year")

admin.site.register(Certificate, CertificateAdmin)
admin.site.register(TempCert)
