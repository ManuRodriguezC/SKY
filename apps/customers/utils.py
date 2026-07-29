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

def get_nominas():
    return (
        Customer.objects
        .exclude(nomina_name__isnull=True)
        .exclude(nomina_name="")
        .values_list(
            "nomina_name",
            flat=True
        )
        .distinct()
        .order_by("nomina_name")
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
        "total": obligation.total_formatted,
    }


def get_email(object):
    if isinstance(object, Customer):
        return object.email
    elif isinstance(object, Obligations):
        return object.customer.email
    return None