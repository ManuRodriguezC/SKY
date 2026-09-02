from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.customers.models import Customer, Obligations, CustomerLog


class Command(BaseCommand):
    help = "Actualiza o registra asociados dentro de SKY"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_name",
            type=str,
            help="Nombre del archivo, debe estar dentro de /files/log/"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        Customer.get_test_customer()
        
        file_name = options["file_name"]

        file_path = Path("/app/files/log") / file_name

        if not file_path.exists():
            self.stderr.write(f"Archivo no encontrado: {file_path}")
            return

        df = pd.read_excel(file_path)

        self.stdout.write(f"Procesando {len(df)} registros")

        created_customers = 0
        updated_customers = 0
        created_obligations = 0
        updated_obligations = 0

        for _, row in df.iterrows():

            document = str(row["AP - Identificación"]).strip()

            city = row["AP - Nombre Ciudad Dir."]
            city = city.strip().title() if pd.notna(city) else None

            try:
                customer, created = Customer.objects.update_or_create(
                    document=document,
                    defaults={
                        "first_name": self.clean_value(row["AP - Nombre"]),
                        "last_name": self.clean_value(row["AP - Apellido"]),
                        "email": self.clean_value(row["AP - Dirección Electrónica"]),
                        "status": self.clean_value(row["AP - Estado como Asociado"]),
                        "type_customer": self.clean_value(row["AP - Nombre Tipo Asociado"]),
                        "nomina_name": self.clean_value(row["AP - Nombre Nomina Asoc."]),
                        "age": self.clean_value(row["AP - Edad"]),
                        "gender": self.clean_value(row["AP - Sexo"]),
                        "phone": self.clean_value(row["AP - Teléfono celular"]),
                        "score": self.clean_value(row["CA - Calificación Crédito"]),
                        "city": city,
                        "contributions": self.clean_value(row["AP - Total Aportes"]),
                    }
                )
            except Exception as e:
                print(f"Error creating/updating customer. Document: {document}. Error: {e}")
                continue

            if created:
                created_customers += 1
                CustomerLog.objects.create(
                    customer=customer,
                    action=CustomerLog.Action.CUSTOMER_CREATED,
                    description="Asociado creado mediante importación de Excel."
                )
            else:
                updated_customers += 1
                CustomerLog.objects.create(
                    customer=customer,
                    action=CustomerLog.Action.CUSTOMER_UPDATED,
                    description="Asociado actualizado mediante importación de Excel."
                )

            try:
                obligation, created = Obligations.objects.update_or_create(
                    customer=customer,
                    num_obligacion=self.clean_value(row["CA - Número de Obligación"]),
                    defaults={
                        "credit_line": self.clean_value(row["CA - Nombre Línea del Crédito"]),
                        "mora_days": self.clean_value(row["CA - Días vencidos"]),
                        "total": self.clean_value(row["TOTAL DE DEUDA"]),
                    }
                )
                
                if created:
                    created_obligations += 1
                    CustomerLog.objects.create(
                        customer=customer,
                        action=CustomerLog.Action.OBLIGATION_CREATED,
                        description=(
                            f"Se registró la obligación "
                            f"{obligation.num_obligacion}."
                        )
                    )
                else:
                    updated_obligations += 1
                    CustomerLog.objects.create(
                        customer=customer,
                        action=CustomerLog.Action.OBLIGATION_UPDATED,
                        description=(
                            f"Se actualizo la obligación "
                            f"{obligation.num_obligacion}."
                        )
                    )

                
            except Exception as e:
                print(f"Error creating/updating customer. Obligation Error: {e}")
                continue


        self.stdout.write(
            self.style.SUCCESS(
                f"""
Clientes creados: {created_customers}
Clientes actualizados: {updated_customers}
Obligaciones creadas: {created_obligations}
Obligaciones actualizadas: {updated_obligations}
                """
            )
        )
    
    def clean_value(self, value):
        return None if pd.isna(value) else value
