from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

class Client(TenantMixin):
    """Model tenanta - każdy tenant to organizacja medyczna"""
    name = models.CharField(max_length=255, help_text='Nazwa organizacji')
    created_on = models.DateTimeField(auto_now_add=True)
    
    
    auto_create_schema = models.BooleanField(default=True)
    auto_drop_schema = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Client (Tenant)'
        verbose_name_plural = 'Clients (Tenants)'
    
    def __str__(self):
        return f"{self.name} ({self.schema_name})"

class Domain(DomainMixin):
    """Model domeny - każdy tenant może mieć wiele domen"""
    pass