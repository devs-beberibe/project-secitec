from django.db import models

from django.contrib.auth.models import User



class Tecs(models.Model):
    
    user = models.ForeignKey(User, verbose_name="tecnico", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    


class User_sec(models.Model):
    
    user = models.ForeignKey(User, verbose_name="ususario_secretaria", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"