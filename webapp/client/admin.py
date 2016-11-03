from django.contrib import admin

# Register your models here.
from client.models import *

class SMSAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'created', 'phone')
    list_filter = ('user',)

admin.site.register(Phone)
admin.site.register(SMS, SMSAdmin)