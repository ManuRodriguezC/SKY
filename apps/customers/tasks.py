import traceback
from pathlib import Path

import pandas as pd

from celery import shared_task
from django.db import transaction

from apps.customers.models import (
    Customer,
    Obligations,
    CustomerLog,
)

@shared_task
def import_obligations(file_name):
    
    print("========== INICIO IMPORTACIÓN ==========")
    print(f"Archivo recibido: {file_name}")

    file_path = Path("/app/files/log") / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Archivo no encontrado: {file_path}"
        )

    df = pd.read_excel(file_path)
    
    print(f"Ruta del archivo: {file_path}")
    print(f"Archivo existe: {file_path.exists()}")

    created_customers = 0
    updated_customers = 0
    created_obligations = 0
    updated_obligations = 0

    with transaction.atomic():

        for _, row in df.iterrows():

            document = str(
                row["AP - Identificación"]
            ).strip()

            city = row["AP - Nombre Ciudad Dir."]

            city = (
                city.strip().title()
                if pd.notna(city)
                else None
            )

            customer, created = (
                Customer.objects.update_or_create(
                    document=document,
                    defaults={
                        "first_name": row["AP - Nombre"],
                        "last_name": row["AP - Apellido"],
                        "email": row[
                            "AP - Dirección Electrónica"
                        ],
                        "status": row[
                            "AP - Estado como Asociado"
                        ],
                        "type_customer": row[
                            "AP - Nombre Tipo Asociado"
                        ],
                        "nomina_name": row[
                            "AP - Nombre Nomina Asoc."
                        ],
                        "age": row["AP - Edad"],
                        "gender": row["AP - Sexo"],
                        "phone": row[
                            "AP - Teléfono celular"
                        ],
                        "score": row[
                            "CA - Calificación Crédito"
                        ],
                        "city": city,
                        "contributions": row[""],
                    },
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

                updated_customers += 1

                CustomerLog.objects.create(
                    customer=customer,
                    action=(
                        CustomerLog.Action
                        .CUSTOMER_UPDATED
                    ),
                    description=(
                        "Asociado actualizado mediante "
                        "importación de Excel."
                    ),
                )

            obligation, created = (
                Obligations.objects.update_or_create(
                    customer=customer,
                    num_obligacion=row[
                        "CA - Número de Obligación"
                    ],
                    defaults={
                        "credit_line": row[
                            "CA - Nombre Línea del Crédito"
                        ],
                        "mora_days": row[
                            "CA - Días vencidos"
                        ],
                        "total": row[
                            "TOTAL DE DEUDA"
                        ],
                    },
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

                updated_obligations += 1

                CustomerLog.objects.create(
                    customer=customer,
                    action=(
                        CustomerLog.Action
                        .OBLIGATION_UPDATED
                    ),
                    description=(
                        f"Se actualizó la obligación "
                        f"{obligation.num_obligacion}."
                    ),
                )

    return {
        "created_customers": created_customers,
        "updated_customers": updated_customers,
        "created_obligations": created_obligations,
        "updated_obligations": updated_obligations,
    }