from django.db import models
from django.urls import reverse


# Create your models here.
class Product(models.Model):
    idx = models.IntegerField()
    name = models.CharField(max_length=120)
    shop_name = models.CharField(max_length=120, default="smokers") # sklep, w którym jest produkt

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'id': self.id})


class Shop(models.Model):
    name = models.CharField(max_length=120)