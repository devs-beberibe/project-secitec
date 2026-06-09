from django.contrib import admin

from .models import SecretarySector, Call, Technician

# Register your models here.

admin.site.register(SecretarySector)
admin.site.register(Call)
admin.site.register(Technician)
