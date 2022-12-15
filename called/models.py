from django.db import models
from django.utils import timezone

# Create your models here.
class Secretary(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Call(models.Model):
    
    STATUS_CALLED = [
        ('OPN', 'abertos'),
        ('IMP', 'emAndamento'),
        ('CLS', 'encerrados'),
    ]

    secretary_sector= models.ForeignKey(Secretary, on_delete=models.CASCADE) 
    problem = models.TextField(max_length=250)
    requester = models.CharField(max_length=100)
    status = models.CharField(max_length=3, choices=STATUS_CALLED, default='OPN')
    date_start = models.DateField(default=timezone.now)
    date_end = models.DateField(default=None, blank=True, null=True)
    
    def __str__(self):
        return Secretary.objects.get(pk=self.secretary_sector.id).name
    
