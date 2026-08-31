from django.db.models import Q

from apps.customers.models import Customer, Obligations
from apps.automations.models import FilterOperator

CUSTOMER_FIELDS = {
    "age": "age",
    "gender": "gender",
    "city": "city",
    "score": "score",
    "status": "status",
    "type_associate": "type_customer",
    "nomina_name": "nomina_name",
}

OBLIGATION_FIELDS = {
    "mora_days": "mora_days",
}

def build_queryset(automation):

    filters = automation.filters.all()

    has_obligation_filter = any(
        filter_obj.field in OBLIGATION_FIELDS
        for filter_obj in filters
    )

    query = Q()

    for filter_obj in filters:

        if filter_obj.field in CUSTOMER_FIELDS:

            field = CUSTOMER_FIELDS[
                filter_obj.field
            ]

            # Si existe al menos un filtro de
            # obligaciones, estamos construyendo
            # el queryset de Obligations.
            if has_obligation_filter:
                field = f"customer__{field}"

        elif filter_obj.field in OBLIGATION_FIELDS:

            field = OBLIGATION_FIELDS[
                filter_obj.field
            ]

        else:
            continue

        query = build_query(
            filter_obj,
            field,
            query,
        )

    if has_obligation_filter:

        return build_obligation_queryset(
            query
        )

    return build_customer_queryset(
        query
    )

def build_query(filter_obj, field, query):

    operator = filter_obj.operator
    value = filter_obj.value
    range_from = filter_obj.range_from
    range_to = filter_obj.range_to

    if operator == FilterOperator.EQ:
        query &= Q(
            **{
                field: value
            }
        )

    elif operator == FilterOperator.GTE:
        query &= Q(
            **{
                f"{field}__gte": value
            }
        )

    elif operator == FilterOperator.LT:
        query &= Q(
            **{
                f"{field}__lt": value
            }
        )

    elif operator == FilterOperator.LTE:
        query &= Q(
            **{
                f"{field}__lte": value
            }
        )

    elif operator == FilterOperator.BETWEEN:

        query &= Q(
            **{
                f"{field}__gte": range_from,
                f"{field}__lte": range_to,
            }
        )

    elif operator == FilterOperator.IN:

        query &= Q(
            **{
                f"{field}__in": value
            }
        )
    
    elif operator == FilterOperator.DIF:
        query &= ~Q(
            **{
                field: value
            }
        )

    return query


def build_customer_queryset(query):

    return Customer.objects.exclude(test=True).filter(query)


def build_obligation_queryset(query):

    return (
        Obligations.objects
        .exclude(customer__test=True)
        .select_related("customer")
        .filter(query)
    )


def get_test_object(automation):
    filter_obj = automation.filters_auto

    if filter_obj.field in CUSTOMER_FIELDS:
        return Customer.objects.filter(
            test=True
        ).first()

    return Obligations.objects.filter(
        customer__test=True
    ).first()