from django import forms
from django.forms import inlineformset_factory


from .models import (
    Automation,
    AutomationFilter,
)


class AutomationForm(forms.ModelForm):

    DAYS = (
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    )
    
    WEEKS = (
        (0, "Semana 1"),
        (1, "Semana 2"),
        (2, "Semana 3"),
        (3, "Semana 4"),
        (4, "Semana 5"),
    )

    days_of_week = forms.MultipleChoiceField(
        choices=DAYS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Días de ejecución",
    )
    
    weeks_of_month = forms.MultipleChoiceField(
        choices=WEEKS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Semana de ejecucion",
    )

    class Meta:
        model = Automation

        fields = (
            "name",
            "description",
            "active",
            "hour",
            "action",
            "subject",
            "body",
            "days_of_week",
            "weeks_of_month",
            "image",
            "date_from",
            "date_to",
            "content_type",
        )

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-base-200"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "textarea textarea-bordered w-full bg-base-200"
                }
            ),

            "active": forms.CheckboxInput(
                attrs={
                    "class": "toggle toggle-success"
                }
            ),

            "hour": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-base-200"
                }
            ),

            "action": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-base-200"
                }
            ),

            "subject": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-base-200",
                    "placeholder": "Asunto del correo"
                }
            ),

            "body": forms.Textarea(
                attrs={
                    "rows": 20,
                    "spellcheck": "false",
                    "class": """
                        textarea
                        textarea-bordered
                        w-full
                        bg-base-200
                        font-mono
                        text-sm
                    """
                }
            ),
            
            "date_from": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": """
                        input
                        input-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),

            "date_to": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": """
                        input
                        input-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),
            
            "image": forms.ClearableFileInput(
                attrs={
                    "class": """
                        file-input
                        file-input-bordered
                        w-full
                        bg-base-200
                    """,
                    "accept": "image/*",
                }
            ),
            
            "content_type": forms.Select(
                attrs={
                    "class": """
                        select
                        select-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),
        }
        

    def clean_days_of_week(self):
        return [
            int(day)
            for day in self.cleaned_data["days_of_week"]
        ]
    
    def clean_weeks_of_month(self):
        return [
            int(week)
            for week in self.cleaned_data["weeks_of_month"]
        ]
    
    def clean(self):
        cleaned_data = super().clean()

        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if (
            date_from and
            date_to and
            date_from > date_to
        ):
            raise forms.ValidationError(
                "La fecha de inicio no puede ser mayor que la fecha final."
            )

        return cleaned_data
        

class AutomationFilterForm(forms.ModelForm):

    class Meta:

        model = AutomationFilter

        fields = (
            "field",
            "operator",
            "value",
            "range_from",
            "range_to",
        )

        widgets = {

            "field": forms.Select(
                attrs={
                    "class": """
                        select
                        select-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),

            "operator": forms.Select(
                attrs={
                    "class": """
                        select
                        select-bordered
                        w-full
                        bg-base-200
                        filter-operator
                    """
                }
            ),

            "value": forms.TextInput(
                attrs={
                    "placeholder": "Valor",
                    "class": """
                        input
                        input-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),

            "range_from": forms.TextInput(
                attrs={
                    "placeholder": "Desde",
                    "class": """
                        input
                        input-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),

            "range_to": forms.TextInput(
                attrs={
                    "placeholder": "Hasta",
                    "class": """
                        input
                        input-bordered
                        w-full
                        bg-base-200
                    """
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        operator = cleaned_data.get("operator")

        value = cleaned_data.get("value")

        range_from = cleaned_data.get("range_from")

        range_to = cleaned_data.get("range_to")

        if operator == "between":

            if not range_from:
                self.add_error(
                    "range_from",
                    "Campo obligatorio."
                )

            if not range_to:
                self.add_error(
                    "range_to",
                    "Campo obligatorio."
                )

        else:

            if not value:
                self.add_error(
                    "value",
                    "Campo obligatorio."
                )

        return cleaned_data


AutomationFilterFormSet = inlineformset_factory(
    Automation,
    AutomationFilter,
    form=AutomationFilterForm,
    extra=0,
    can_delete=True,
)

def get_automation_filter_formset(extra=0):

    return inlineformset_factory(
        Automation,
        AutomationFilter,
        form=AutomationFilterForm,
        extra=extra,
        can_delete=True,
    )