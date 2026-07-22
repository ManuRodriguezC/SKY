from django.utils import timezone
from django.db.models import Q
from math import ceil

from apps.automations.models import Automation
from apps.automations.services.filter_engine import build_queryset


def get_pending_automation():
    now = timezone.localtime()
    
    today = now.date()
    hour = now.hour
    weekday = now.weekday()
    week = ceil(now.day / 7)

    automations = Automation.objects.exclude(deleted=True).filter(
        active=True,
        hour=hour,
        days_of_week__contains=[weekday],
        weeks_of_month__contains=[week],
    ).filter(
        Q(date_from__isnull=True) | Q(date_from__lte=today),
        Q(date_to__isnull=True) | Q(date_to__gte=today),
    )
    
    return automations


def process_pending_automations():
    
    automations = get_pending_automation()
    
    for automation in automations:
        execute_automation(automation)
        

def execute_automation(automation):
    objects = build_queryset(automation)

    action = get_action()
    
    for object in objects:
        action(automation, object)
    

def get_action():
    from apps.automations.tasks import send_email_task
    
    return send_email_task