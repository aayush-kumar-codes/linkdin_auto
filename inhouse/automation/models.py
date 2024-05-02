from django.db import models
from django.contrib.postgres.fields import ArrayField


class LinkedInJobs(models.Model):
    email = models.EmailField(null=True, blank=True)
    skills = models.TextField(null=True)
    linkedin_profile_link = models.TextField(null=True, blank=True)
    post_profile = models.TextField(null=False)
    post_content = models.TextField(null=False)
    urn_id = models.TextField(unique=True)
