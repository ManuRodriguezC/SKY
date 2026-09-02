from celery import shared_task
import logging

from apps.automations.services.automation_service import process_pending_automations
from apps.automations.services.send_service import send_customer_email
from apps.automations.utils import create_content
from apps.automations.models import Automation
from apps.automations.services.automation_service import execute_automation

logger = logging.getLogger(__name__)

@shared_task
def check_automations():
    process_pending_automations()


def send_email_task(
    automation,
    object,
    connection
):

    content = create_content(automation, object)

    send_customer_email(
        object=object,
        automation=automation,
        content=content,
        connection=connection
    )

@shared_task
def execute_auto(automation_id):
    automation = Automation.objects.filter(id=automation_id).first()

    if not automation:
        return
    logger.info(f"Se ejecuta la automatizacion {automation}")
    
    execute_automation(
        automation=automation,
    )
