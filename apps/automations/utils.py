from django.template import Template, Context

from apps.customers.models import Customer, Obligations
from apps.customers.utils import build_customer_context, build_obligation_context

def build_context(obj):

    if isinstance(obj, Customer):
        return build_customer_context(obj)

    if isinstance(obj, Obligations):
        return build_obligation_context(obj)

    raise ValueError(
        f"Tipo no soportado: {type(obj)}"
    )


def create_content(automation, object):
    template = Template(
        automation.body
    )
    context = Context(build_context(object))

    return template.render(
        context
    )
    