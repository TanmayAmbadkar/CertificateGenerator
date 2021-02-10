from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
import hashlib
import pytz
# Create your models here.
class LoginToken(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default="xyz")
    expiry = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user.username} {self.token}"

    def save(self, *args, **kwargs):
        local_tz = pytz.timezone('Asia/Kolkata')
        self.expiry = datetime.now()+timedelta(days=1)
        token = f"{self.user.username} {str(self.expiry)}"
        obj = hashlib.sha1(token.encode("utf-8"))
        self.token = obj.hexdigest()

        super(LoginToken, self).save(*args, **kwargs)

    def is_valid(self):
        if self.expiry>timezone.now():
            return True
        else:
            return False
