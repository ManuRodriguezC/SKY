import traceback
from pathlib import Path

import pandas as pd

from celery import shared_task
from django.db import transaction


from apps.customers.models import (
    Customer,
    Obligations,
    CustomerLog,
    ImportExecution
)
from apps.customers.utils import (
    get_data,
    get_data_obligations,
    get_data_customer,
    get_document,
    get_city,
    clean_value,
    values_are_equal,
)

@shared_task
def import_customers(file_name, import_id):
    import_execution = ImportExecution.objects.get(id=import_id)
    import_execution.mark_processing()
    
    print("========== INICIO IMPORTACIÓN ==========")
    print(f"Archivo recibido: {file_name}")

    file_path = Path("/app/files/log") / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Archivo no encontrado: {file_path}"
        )

    df = pd.read_excel(file_path)

    created_customers = 0
    updated_customers = 0

    try:

        with transaction.atomic():

            for _, row in df.iterrows():
                document = get_document(row, "A_NUMNIT")
                city = get_city(row, "N_CIUDAD")
                data = get_data_customer(row, city)

                customer, created = (
                    Customer.objects.update_or_create(
                        document=document,
                        defaults=data,
                    )
                )

                if created:

                    created_customers += 1

                    CustomerLog.objects.create(
                        customer=customer,
                        action=(
                            CustomerLog.Action
                            .CUSTOMER_CREATED
                        ),
                        description=(
                            "Asociado creado mediante "
                            "importación de Excel."
                        ),
                    )

                else:

                    changed = False

                    for field, new_value in data.items():
                        current_value = getattr(customer, field)

                        if current_value != new_value:
                            changed = True
                            setattr(customer, field, new_value)

                    if changed:
                        customer.save()
                        updated_customers += 1

                        CustomerLog.objects.create(
                            customer=customer,
                            action=CustomerLog.Action.CUSTOMER_UPDATED,
                            description=(
                                "Asociado actualizado mediante "
                                "importación de Excel."
                            ),
                        )

        detail = {}

        if created_customers:
            detail["Asociados creados"] = created_customers

        if updated_customers:
            detail["Asociados actualizados"] = updated_customers

        if not detail:
            detail["Resultado"] = "No se registró ningún cambio."
        
        detail_text = "\n".join(
            f"{key}: {value}"
            for key, value in detail.items()
        )
        
        import_execution.mark_success(detail_text)

    except Exception as e:
        print(e)
        import_execution.mark_failed(f"Se presento un fallo: {e}")


@shared_task
def import_obligations(file_name, import_id):
    import_execution = ImportExecution.objects.get(id=import_id)
    import_execution.mark_processing()
    
    print("========== INICIO IMPORTACIÓN ==========")
    print(f"Archivo recibido: {file_name}")

    file_path = Path("/app/files/log") / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Archivo no encontrado: {file_path}"
        )

    df = pd.read_excel(file_path)

    created_customers = 0
    updated_customers = 0
    created_obligations = 0
    updated_obligations = 0

    try:

        with transaction.atomic():

            for _, row in df.iterrows():
                document = get_document(row, "AP - Identificación")
                city = get_city(row, "AP - Nombre Ciudad Dir.")
                data = get_data(row, city)

                customer, created = (
                    Customer.objects.update_or_create(
                        document=document,
                        defaults=data,
                    )
                )

                if created:

                    created_customers += 1

                    CustomerLog.objects.create(
                        customer=customer,
                        action=(
                            CustomerLog.Action
                            .CUSTOMER_CREATED
                        ),
                        description=(
                            "Asociado creado mediante "
                            "importación de Excel."
                        ),
                    )

                else:

                    changed = False

                    for field, new_value in data.items():
                        current_value = getattr(customer, field)

                        if current_value != new_value:
                            changed = True
                            setattr(customer, field, new_value)

                    if changed:
                        customer.save()
                        updated_customers += 1

                        CustomerLog.objects.create(
                            customer=customer,
                            action=CustomerLog.Action.CUSTOMER_UPDATED,
                            description=(
                                "Asociado actualizado mediante "
                                "importación de Excel."
                            ),
                        )

                num_obligation = clean_value(
                    row["CA - Número de Obligación"]
                )
                
                data_obligation = get_data_obligations(row)
                
                obligation, created = (
                    Obligations.objects.get_or_create(
                        customer=customer,
                        num_obligacion=num_obligation,
                        defaults=data_obligation,
                    )
                )

                if created:

                    created_obligations += 1

                    CustomerLog.objects.create(
                        customer=customer,
                        action=(
                            CustomerLog.Action
                            .OBLIGATION_CREATED
                        ),
                        description=(
                            f"Se registró la obligación "
                            f"{obligation.num_obligacion}."
                        ),
                    )

                else:
                    changes = []
                    for field, new_value in data_obligation.items():

                        old_value = getattr(
                            obligation,
                            field
                        )
                        if not values_are_equal(old_value, new_value):
                            changes.append(
                                f"{field}: '{old_value}' → '{new_value}'"
                            )

                            setattr(
                                obligation,
                                field,
                                new_value
                            )

                    if changes:

                        obligation.save()

                        updated_obligations += 1

                        CustomerLog.objects.create(
                            customer=customer,
                            action=CustomerLog.Action.OBLIGATION_UPDATED,
                            description=(
                                f"Se actualizó la obligación "
                                f"{obligation.num_obligacion}.\n"
                                + "\n".join(changes)
                            ),
                        )

        detail = {}

        if created_customers:
            detail["Asociados creados"] = created_customers

        if updated_customers:
            detail["Asociados actualizados"] = updated_customers

        if created_obligations:
            detail["Obligaciones creadas"] = created_obligations

        if updated_obligations:
            detail["Obligaciones actualizadas"] = updated_obligations

        if not detail:
            detail["Resultado"] = "No se registró ningún cambio."
        
        detail_text = "\n".join(
            f"{key}: {value}"
            for key, value in detail.items()
        )
        
        import_execution.mark_success(detail_text)

    except Exception as e:
        
        import_execution.mark_failed(f"Se presento un fallo: {e}")
