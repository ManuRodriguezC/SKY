from django.core.mail import send_mail
from django.template import Context, Template

from celery import shared_task

from apps.automations.services.automation_service import process_pending_automations
from apps.automations.services.send_service import send_customer_email
from apps.automations.utils import create_content
from apps.automations.models import Automation
from apps.automations.services.automation_service import execute_automation


@shared_task
def check_automations():
    process_pending_automations()


@shared_task
def send_email_task(
    automation,
    object,
):

    content = create_content(automation, object)

    send_customer_email(
        object=object,
        automation=automation,
        content=content,
    )

@shared_task
def execute_auto(automation_id):
    automation = Automation.objects.get(id=automation_id)
    if automation:
        execute_automation(automation)