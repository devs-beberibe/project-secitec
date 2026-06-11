from django.contrib import admin
from .models import (
    MaintenanceSheet,
    Components,
    ComponentStatus,
)

admin.site.register(MaintenanceSheet)
admin.site.register(Components)
admin.site.register(ComponentStatus)
