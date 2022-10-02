from tarfile import PAX_FIELDS
from telnetlib import STATUS
from unicodedata import name
from django.db import models

# Create your models here.
class Secretary(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Call(models.Model):
    
    STATUS_CALLED = [
        ('OPN', 'aberto'),
        ('INP', 'executando'),
        ('CLS', 'encerrado'),
    ]

    secretary_sector= models.ForeignKey(Secretary, on_delete=models.CASCADE) 
    problem = models.TextField(max_length=250)
    requester = models.CharField(max_length=100)
    status = models.CharField(max_length=3, choices=STATUS_CALLED, default='OPN')
    
    def __str__(self):
        #return self.problem
        return Secretary.objects.get(pk=self.secretary_sector.id).name
    