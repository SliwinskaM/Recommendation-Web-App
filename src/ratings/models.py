from django.db import models

# Create your models here.
class Rating(models.Model):
    user = models.CharField(max_length=120)
    product = models.CharField(max_length=500)
    score = models.IntegerField()
    shop = models.CharField(max_length=120, default='smoker')