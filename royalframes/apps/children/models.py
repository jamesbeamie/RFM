from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify

from royalframes.apps.authentication.models import User
from cloudinary.models import CloudinaryField


class Children(models.Model):
    """
        Each Article model schema
    """
    image_path = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(db_index=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.title
