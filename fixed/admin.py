from django.contrib import admin
from .models import (
    MaintenanceSheet,
    Component,
    ComponentStatus,
)

admin.site.register(MaintenanceSheet)
admin.site.register(Component)
admin.site.register(ComponentStatus)
