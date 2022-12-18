from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model 

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
    solution = models.TextField(max_length=250, null=True, blank=True)
    
    def __str__(self):
        return Secretary.objects.get(pk=self.secretary_sector.id).name
    

class Tecnico(models.Model):
    
    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='tecnico',        
    ) 

    called = models.ManyToManyField(Call)#, related_name="call_tecnico")
    
    def __str__(self) -> str:
        return f"Perfil de {self.user.username}"

