from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Phone(models.Model):
    user        = models.ForeignKey(User)
    number      = models.CharField(max_length = 1024, unique = True)
    created     = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.number
    
class SMS(models.Model):
    user        = models.ForeignKey(User)
    created     = models.DateTimeField(auto_now = True)
    reported    = models.DateTimeField(auto_now = True)
    phone       = models.ForeignKey(Phone)
    body        = models.CharField(max_length = 4096)
    sender      = models.CharField(max_length = 1024)

    def __unicode__(self):
        return self.body

    class Meta:
        ordering = ['-created']






