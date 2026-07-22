from .models import Customer, Obligations


def get_type_customers():
    return (
        Customer.objects
        .exclude(type_customer__isnull=True)
        .exclude(type_customer="")
        .values_list(
            "type_customer",
            flat=True,
        )
        .distinct()
        .order_by("type_customer")
    )


def get_citys():
    return (
        Customer.objects
        .exclude(city__isnull=True)
        .exclude(city="")
        .values_list(
            "city",
            flat=True,
        )
        .distinct()
        .order_by("city")
    )


def get_gender():
    return [
        ("F", "Femenino"),
        ("M", "Masculino"),
    ]
    
    
def get_status_customers():
    return (
        Customer.objects
        .exclude(status__isnull=True)
        .exclude(status="")
        .values_list(
            "status",
            flat=True,
        )
        .distinct()
        .order_by("status")
    )


def build_customer_context(
    customer,
):
    return {
        "nombre": customer.first_name,
        "apellido": customer.last_name,
        "ciudad": customer.city,
    }
    
def build_obligation_context(
    obligation,
):
    return {
        "nombre": obligation.customer.first_name,
        "apellido": obligation.customer.last_name,
        "obligacion": obligation.num_obligacion,
        "mora": obligation.mora_days,
        "ciudad": obligation.customer.city,
    }


def get_email(object):
    if isinstance(object, Customer):
        return object.email
    if isinstance(object, Obligations):
        return object.customer.email
    return None