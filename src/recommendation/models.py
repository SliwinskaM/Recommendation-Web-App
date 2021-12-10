from django.db import models


# Create your models here.
class Recommendation(models.Model):
    username = models.CharField(max_length=120)
    products = models.CharField(max_length=500)
    shop = models.CharField(max_length=120)