from django.contrib import admin
from .models import Client, Domain

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'created_on', 'auto_create_schema')
    list_filter = ('auto_create_schema', 'auto_drop_schema', 'created_on')
    search_fields = ('name', 'schema_name')
    readonly_fields = ('created_on',)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary', 'tenant')
    search_fields = ('domain', 'tenant__name')