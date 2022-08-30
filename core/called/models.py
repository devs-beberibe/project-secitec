from django.db import models

# Create your models here.
class Secretary(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Call(models.Model):

    secretary_sector= models.ForeignKey(Secretary, on_delete=models.CASCADE) 
    problem = models.TextField(max_length=250)
    requester = models.CharField(max_length=100)
    
    def __str__(self):
        #return self.problem
        return Secretary.objects.get(id=1).name, self.problem
    