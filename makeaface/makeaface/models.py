from django.db import models


class Lastface(models.Model):
    owner = models.CharField(max_length=60, primary_key=True)
    face = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now=True)


class Favoriteface(models.Model):
    favorited = models.CharField(max_length=60)
    favoriter = models.CharField(max_length=60)
    lastface = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('favorited', 'favoriter'),)
