from django.contrib import admin

from .models import Secretary, Call, Technician

# Register your models here.

admin.site.register(Secretary)
admin.site.register(Call)
admin.site.register(Technician)
