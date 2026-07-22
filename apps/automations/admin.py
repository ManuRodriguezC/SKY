from django.contrib import admin
from .models import Automation, AutomationFilter

@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(AutomationFilter)
class AutomationFilterAdmin(admin.ModelAdmin):
    list_display = ('automation', 'field', 'operator')
    search_fields = ('automation', 'field', 'operator')
