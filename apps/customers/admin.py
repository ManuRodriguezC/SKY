from django.contrib import admin
from .models import Customer, Obligations

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'document', 'city')
    search_fields = ('first_name', 'last_name', 'document')
    
@admin.register(Obligations)
class ObligationsAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'num_obligacion', 'credit_line', 'mora_days')
    search_fields =  ('num_obligacion', 'credit_line', 'mora_days')
    
    @admin.display(description="Cliente")
    def customer_name(self, obj):
        return obj.customer.first_name