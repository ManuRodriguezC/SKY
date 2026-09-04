import pandas as pd
from datetime import datetime, date

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

def get_data(row, city):
    data = {
        "first_name": clean_value(
            row["AP - Nombre"]
        ),
        "last_name": clean_value(
            row["AP - Apellido"]
        ),
        "email": clean_value(
            row["AP - Dirección Electrónica"]
        ),
        "status": clean_value(
            row["AP - Estado como Asociado"]
        ),
        "type_customer": clean_value(
            row["AP - Nombre Tipo Asociado"]
        ),
        "nomina_name": clean_value(
            row["AP - Nombre Nomina Asoc."]
        ),
        "age": clean_value(
            row["AP - Edad"]
        ),
        "gender": clean_value(
            row["AP - Sexo"]
        ),
        "phone": clean_value(
            row["AP - Teléfono celular"]
        ),
        "score": clean_value(
            row["CA - Calificación Crédito"]
        ),
        "city": city,
        "contributions": clean_value(
            row["AP - Total Aportes"]
        ),
    }
    return data

def get_data_customer(row, city):
    data = {
        "first_name": clean_value(
            row["NOMBRE"]
        ),
        "last_name": clean_value(
            row["APELLIDO"]
        ),
        "email": clean_value(
            row["CORREO"]
        ),
        "status": "",
        "type_customer": "",
        "nomina_name": clean_value(
            row["N_NOMINA"]
        ),
        "age": calculate_age(row["FECHA NACIMIENTO"]),
        "gender": "",
        "phone": clean_value(
            row["T_TERCEL"]
        ),
        "score": "",
        "city": city,
        "contributions": 0,
    }
    return data

def get_data_obligations(row):
    return {
        "credit_line": clean_value(row[
            "CA - Nombre Línea del Crédito"
        ]),
        "mora_days": clean_value(row[
            "CA - Días vencidos"
        ]),
        "total": clean_value(row[
            "TOTAL DE DEUDA"
        ]),
    }

def get_document(row, name):
    return str(
        clean_value(row[name])
    ).strip()

def get_city(row, name):
    city = row[name]

    return (
        city.strip().title()
        if pd.notna(city)
        else None
    )

def clean_value(value):
    return None if pd.isna(value) else value

def values_are_equal(old_value, new_value):
    if old_value is None and new_value is None:
        return True

    if old_value is None or new_value is None:
        return False

    try:
        if isinstance(old_value, int):
            new_value = int(new_value)
            return int(old_value) == int(new_value)
        elif isinstance(old_value, float):
            return float(old_value) == float(new_value)
    except (TypeError, ValueError):
        return str(old_value).strip() == str(new_value).strip()

def calculate_age(birth_date):
    try:
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()

        elif isinstance(birth_date, str):
            birth_date = datetime.strptime(
                birth_date,
                "%d/%m/%Y"
            ).date()

        today = date.today()

        age = today.year - birth_date.year

        if (today.month, today.day) < (
            birth_date.month,
            birth_date.day
        ):
            age -= 1

        return age
    except Exception:
        return 0
