from rest_framework import serializers
from store.models import *


class TempCertSerializer(serializers.ModelSerializer):

    class Meta:

        model = TempCert
        fields = '__all__'
