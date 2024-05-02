from django.contrib import admin
from .models import LinkedInJobs, EmailSettings

# Register your models here.

admin.site.register(LinkedInJobs)
admin.site.register(EmailSettings)
