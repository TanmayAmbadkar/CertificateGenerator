from rest_framework import serializers
from store.models import *


class TempCertSerializer(serializers.ModelSerializer):

    class Meta:

        model = TempCert
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    cert_url = serializers.SerializerMethodField('get_cert_url')

    class Meta:

        model = Certificate
        fields = '__all__'
    
    def get_cert_url(self, obj):
        try:
            return self.context['request'].build_absolute_uri(obj.file.path)
        except Exception as e:
            return None
