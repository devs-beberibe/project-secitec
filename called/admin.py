from django.contrib import admin

from .models import Secretary, Call,Tecnico

# Register your models here.

admin.site.register(Secretary)
admin.site.register(Call)
admin.site.register(Tecnico)