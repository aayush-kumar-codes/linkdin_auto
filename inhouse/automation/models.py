from django.db import models


class LinkedInJobs(models.Model):
    email = models.EmailField(null=False)
    skills = models.TextField(null=True)
    linkedin_profile_link = models.TextField(null=True, blank=True)
    post_profile = models.TextField(null=False)
    post_content = models.TextField(null=False)
    urn_id = models.TextField(unique=True)
