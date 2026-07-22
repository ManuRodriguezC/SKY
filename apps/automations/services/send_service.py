from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage

from apps.automations.models import EmailFormat, AutomationExecution
from apps.customers.utils import get_email
from email.mime.image import MIMEImage



def send_customer_email(
    object,
    automation,
    content,
):
    if (
        automation.content_type ==
        EmailFormat.TEXT
    ):

        send_text_email(
            object,
            automation,
            content,
        )

    send_html_email(
        object,
        automation,
        content,
    )
    
    
def send_text_email(
    object,
    automation,
    content,
):
    email = get_email(object)

    send_email = EmailMessage(
        subject=automation.subject,
        body=content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            email
        ],
    )

    if automation.image:

        with automation.image.storage.open(
            automation.image.name,
            "rb",
        ) as file:

            send_email.attach(
                filename=automation.image.name.split("/")[-1],
                content=file.read(),
                mimetype="image/png",
            )

    try:
        send_email.send()
        AutomationExecution.register_success(
            automation,
            object,
            content
        )
    except:
        AutomationExecution.register_failed(
            automation,
            object,
            content
        )

def send_html_email(
    email,
    automation,
    content,
):

    send_email = EmailMultiAlternatives(
        subject=automation.subject,
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            email
        ],
    )

    if automation.image:

        content = f"""
            <img
                src="cid:automation-image"
                style="
                    width:100%;
                    display:block;
                    margin-bottom:20px;
                "
            >

            {content}
        """

    send_email.attach_alternative(
        content,
        "text/html",
    )

    if automation.image:

        with automation.image.open("rb") as file:

            image = MIMEImage(
                file.read()
            )

            image.add_header(
                "Content-ID",
                "<automation-image>",
            )

            image.add_header(
                "Content-Disposition",
                "inline",
                filename=automation.image.name,
            )

            send_email.attach(image)

    try:
        send_email.send()
        AutomationExecution.register_success(
            automation,
            object,
            content
        )
        print("En envia y se guarda")
    except:
        AutomationExecution.register_failed(
            automation,
            object,
            content
        )